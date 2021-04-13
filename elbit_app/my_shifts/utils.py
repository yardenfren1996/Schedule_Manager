import datetime
from . import heaputil
import re
import json
import random
from random import sample
import heapq

from django.contrib.auth.models import User

from .models import WorkerProfileInfo, Shift

SHIFT_NUMBER_RANDOM = 4

SHIFT_OPTIONS = ['Morning', 'After Noon', 'Night']
CAPACITY_OPTIONS = {'regular_day_morning': 9, 'regular_day_noon': 8,
                    'night': 7, 'special_day': 5, 'friday_morning': 8, }
VALUE_OPTIONS = {'regular_day_morning': 400, 'regular_day_noon': 320, 'regular_day_night': 350,
                 'special_day': 500, 'friday_noon': 400, }
WEEK_DAYS = ['Sunday', 'Monday', 'Tuesday', 'Wednesday', 'Thursday', 'Friday', 'Saturday']

TOTAL_SHIFTS_MAT = [['Sunday_Morning', 'Monday_Morning', 'Tuesday_Morning', 'Wednesday_Morning', 'Thursday_Morning',
                     'Friday_Morning', 'Saturday_Morning'], ['Sunday_After Noon', 'Monday_After Noon',
                                                             'Tuesday_After Noon', 'Wednesday_After Noon',
                                                             'Thursday_After Noon', 'Friday_After Noon',
                                                             'Saturday_After Noon'], ['Sunday_Night',
                                                                                      'Monday_Night', 'Tuesday_Night',
                                                                                      'Wednesday_Night',
                                                                                      'Thursday_Night', 'Friday_Night',
                                                                                      'Saturday_Night'], ]

CAPACITY_AND_VALUES = {
    'Sunday_Morning': [CAPACITY_OPTIONS['regular_day_morning'], VALUE_OPTIONS['regular_day_morning']],
    'Sunday_After Noon': [CAPACITY_OPTIONS['regular_day_noon'], VALUE_OPTIONS['regular_day_noon']],
    'Sunday_Night': [CAPACITY_OPTIONS['night'], VALUE_OPTIONS['regular_day_night']],
    'Monday_Morning': [CAPACITY_OPTIONS['regular_day_morning'], VALUE_OPTIONS['regular_day_morning']],
    'Monday_After Noon': [CAPACITY_OPTIONS['regular_day_noon'], VALUE_OPTIONS['regular_day_noon']],
    'Monday_Night': [CAPACITY_OPTIONS['night'], VALUE_OPTIONS['regular_day_night']],
    'Tuesday_Morning': [CAPACITY_OPTIONS['regular_day_morning'], VALUE_OPTIONS['regular_day_morning']],
    'Tuesday_After Noon': [CAPACITY_OPTIONS['regular_day_noon'], VALUE_OPTIONS['regular_day_noon']],
    'Tuesday_Night': [CAPACITY_OPTIONS['night'], VALUE_OPTIONS['regular_day_night']],
    'Wednesday_Morning': [CAPACITY_OPTIONS['regular_day_morning'], VALUE_OPTIONS['regular_day_morning']],
    'Wednesday_After Noon': [CAPACITY_OPTIONS['regular_day_noon'], VALUE_OPTIONS['regular_day_noon']],
    'Wednesday_Night': [CAPACITY_OPTIONS['night'], VALUE_OPTIONS['regular_day_night']],
    'Thursday_Morning': [CAPACITY_OPTIONS['regular_day_morning'], VALUE_OPTIONS['regular_day_morning']],
    'Thursday_After Noon': [CAPACITY_OPTIONS['regular_day_noon'], VALUE_OPTIONS['regular_day_noon']],
    'Thursday_Night': [CAPACITY_OPTIONS['night'], VALUE_OPTIONS['regular_day_night']],
    'Friday_Morning': [CAPACITY_OPTIONS['friday_morning'], VALUE_OPTIONS['regular_day_morning']],
    'Friday_After Noon': [CAPACITY_OPTIONS['special_day'], VALUE_OPTIONS['friday_noon']],
    'Friday_Night': [CAPACITY_OPTIONS['night'], VALUE_OPTIONS['special_day']],
    'Saturday_Morning': [CAPACITY_OPTIONS['special_day'], VALUE_OPTIONS['special_day']],
    'Saturday_After Noon': [CAPACITY_OPTIONS['special_day'], VALUE_OPTIONS['special_day']],
    'Saturday_Night': [CAPACITY_OPTIONS['night'], VALUE_OPTIONS['special_day']]}


def get_next_sunday_date():
    today_date = datetime.date.today()
    if today_date.weekday() == 6:
        next_sunday = today_date + datetime.timedelta(7)
    else:
        while today_date.weekday() != 6:
            today_date += datetime.timedelta(1)
        next_sunday = today_date

    return next_sunday


def get_next_week_dates(sunday):
    week_dates = []
    for i in range(7):
        week_dates.append(sunday + datetime.timedelta(i))
    return week_dates


def get_capacity_and_value(shift_date: datetime, shift_time: str):
    if 0 <= shift_date.weekday() <= 4 or shift_date.weekday() == 6:
        if shift_time == SHIFT_OPTIONS[0]:
            return CAPACITY_OPTIONS['regular_day_morning'], VALUE_OPTIONS['regular_day_morning']
        if shift_time == SHIFT_OPTIONS[1]:
            return CAPACITY_OPTIONS['regular_day_noon'], VALUE_OPTIONS['regular_day_noon']
        if shift_time == SHIFT_OPTIONS[2]:
            return CAPACITY_OPTIONS['night'], VALUE_OPTIONS['regular_day_night']
    if shift_date.weekday() == 5:
        if shift_time == SHIFT_OPTIONS[0]:
            return CAPACITY_OPTIONS['friday_morning'], VALUE_OPTIONS['regular_day_morning']
        if shift_time == SHIFT_OPTIONS[1]:
            return CAPACITY_OPTIONS['special_day'], VALUE_OPTIONS['friday_noon']
        if shift_time == SHIFT_OPTIONS[2]:
            return CAPACITY_OPTIONS['night'], VALUE_OPTIONS['special_day']
    else:
        if shift_time == SHIFT_OPTIONS[2]:
            return CAPACITY_OPTIONS['night'], VALUE_OPTIONS['special_day']
        else:
            return CAPACITY_OPTIONS['special_day'], VALUE_OPTIONS['special_day']


def create_shifts(values: str, user: User):
    values = json.loads(values)
    publish_time = values['publish_date']
    shifts_dict = values['shifts']
    for key in shifts_dict:
        arr = key.split(',')
        shift_date = datetime.datetime.strptime(arr[0][1:], '%Y-%m-%d')
        shift_time = arr[1][:-1]
        capacity_and_value = get_capacity_and_value(shift_date, shift_time)
        shift = Shift(user=user, date=shift_date, shift_time=shift_time, capacity=capacity_and_value[0],
                      value=capacity_and_value[1], creation_time=publish_time)
        shift.save()


def delete_previous_shifts(user: User):
    next_sunday = get_next_sunday_date()
    next_saturday = next_sunday + datetime.timedelta(6)
    Shift.objects.filter(date__gte=next_sunday, date__lte=next_saturday, user=user).delete()


def get_list_of_workers_per_day():
    result = {}
    next_sunday = get_next_sunday_date()
    for i in range(7):
        week_date = next_sunday + datetime.timedelta(i)
        for j in range(3):
            result["{}_{}".format(WEEK_DAYS[i], SHIFT_OPTIONS[j])] = Shift.objects.filter(date=week_date,
                                                                                          shift_time=SHIFT_OPTIONS[
                                                                                              j]).values_list(
                'user_id', flat=True)
    for key, value in result.items():
        users_list = []
        for i in range(len(value)):
            users_list.append(User.objects.get(id=value[i]).username)
        result[key] = users_list

    return result


######################
# THE MAIN ALGORITHM #
######################

############### STEPS ###################
'''
1. GET THE RECEVED DATE AND ORGNIZED IT MY ONE TO MANY (ex:  (2020-11-15,night): [Yarden, Or, Ido, Shachar, Tal])
        that means that i have one dictionary that contains 21 keys Shift objects (date,shift_time), and each dictionary 
        has his own list of workers that are able to work on that shift.
2. GET THE CAPACITY AND THE VALUE OF EACH SHIFT
3. CREATE NEW MIN-HEAP WITH THE MONEY-VALUE OF EACH WORKER THAT HAS SUBMITTED SHIFTS 
4. CREATE MIN-HEAP FOR THE SHIFTS WITH THE RATIO BETWEEN THE  NUMBER OF ASSINMENTS TO THE CAPACITY
5. IF THE RATIO IS LOWER THAN 1 THAN ASSIGN WITH NO COUNTABLE TO THE VALUE
        in case that the number of signers is lower -> than assign to each Shift the members of it and add the value of
        the shift to their total value
        **while assignment remove the closer shifts that is available (like if worker gets friday night he cant work
          at noon either at the morning after
5. CHECK IF THE CAPACITY IS FULL THE DELETE FROM HEAP
6. CONTINUE TO ASSIGN WORKERS TO THE SHIFTS TILL ALL THE CAPACITY IS FULL
        in that part we need to consider the value heap in order to get the equal total money-value to e.o
7. IN THE END EACH SHIFT HAS THIS DATA:
        as dict -> {capacity,workers,names_of_workers:[]}
8. THE DATA BELOW IS:
        as dict: {workers_spare_shifts:[],avg.salary, commends:{name:commend},}
'''


def make_fake_shifts_for_test():
    next_sunday = get_next_sunday_date()
    next_week_days = []
    for i in range(7):
        next_week_days.append(next_sunday + datetime.timedelta(i))
    workers_list = WorkerProfileInfo.objects.values_list('worker')
    for worker_id in workers_list:
        user = User.objects.get(id=worker_id[0])
        shift_date_list = sample(range(0, 7), SHIFT_NUMBER_RANDOM)
        for i in range(SHIFT_NUMBER_RANDOM):
            shift_time = SHIFT_OPTIONS[random.randint(0, 2)]
            shift_date = next_week_days[shift_date_list[i]]

            capacity_and_value = get_capacity_and_value(shift_date, shift_time)
            shift = Shift(user=user, date=shift_date, shift_time=shift_time, capacity=capacity_and_value[0],
                          value=capacity_and_value[1], creation_time=0)
            shift.save()


def get_shifts_list():
    next_sunday = get_next_sunday_date()
    next_saturday = next_sunday + datetime.timedelta(6)
    shifts_list = Shift.objects.filter(date__gte=next_sunday, date__lte=next_saturday)
    return shifts_list


def sort_list(shifts_dict):
    shift_capacity = []
    for key, value in shifts_dict.items():
        shift_capacity.append((key, (len(value) / CAPACITY_AND_VALUES[key][0])))

    return shift_capacity


def get_worker_dict():
    workers_list = User.objects.all()
    worker_dict = {}
    for workers in workers_list:
        worker_dict[workers.username] = 0
    return worker_dict


def blocked_shifts_by_shift(shift_name):
    arr = shift_name.split('_')
    shift_day = arr[0]
    shift_time = arr[1]
    blocked_shifts = []
    if shift_time == SHIFT_OPTIONS[0]:
        blocked_shifts.append(shift_day + "_" + SHIFT_OPTIONS[1])
        blocked_shifts.append(shift_day + "_" + SHIFT_OPTIONS[2])
        if shift_day != WEEK_DAYS[0]:
            blocked_shifts.append(WEEK_DAYS[WEEK_DAYS.index(shift_day) - 1] + "_" + SHIFT_OPTIONS[2])

    if shift_time == SHIFT_OPTIONS[1]:
        blocked_shifts.append(shift_day + "_" + SHIFT_OPTIONS[0])
        blocked_shifts.append(shift_day + "_" + SHIFT_OPTIONS[2])

    if shift_time == SHIFT_OPTIONS[2]:
        blocked_shifts.append(shift_day + "_" + SHIFT_OPTIONS[0])
        blocked_shifts.append(shift_day + "_" + SHIFT_OPTIONS[1])
        if shift_day != WEEK_DAYS[6]:
            blocked_shifts.append(WEEK_DAYS[WEEK_DAYS.index(shift_day) + 1] + "_" + SHIFT_OPTIONS[0])

    return blocked_shifts


def make_schedule():
    list_of_ready = []
    shifts_dict = get_list_of_workers_per_day()  # dict of shift and list of names
    worker_salary_dict = get_worker_dict()  # names of workers with values = 0
    shift_capacity = sort_list(shifts_dict)  # list of tuples (x,y) | x = shift as string ; y = assingers/capacity

    for value in shift_capacity:
        heaputil.add_task(value[0], value[1])  # create min-Heap

    for i in range(21):  # for all shifts
        shift = heaputil.pop_task()  # get min
        shift_name = shift[0]
        list_of_ready.append(shift_name)
        workers = shifts_dict[shift_name]  # get the list of workers in the same shift
        blocked_shifts = list(set(blocked_shifts_by_shift(shift_name)).difference(
            list_of_ready))  # get the blocked shifts that worker who worked on the shift cannot work on the blocked
        if shift[1] <= 1:  # if the ratio is smaller than 1 means that we need to assign all the workers to that shift
            for blocked in blocked_shifts:
                blocking_workers = shifts_dict[blocked]
                need_to_remove = list(set(workers).intersection(blocking_workers))
                # print("the following workers :{} are need to remove from {} shift".format(need_to_remove, blocked))
                if len(need_to_remove) > 0:
                    # print("workers on {} shift : {}".format(blocked, shifts_dict[blocked]))
                    heaputil.remove_task(blocked)
                    heaputil.add_task(blocked, len(shifts_dict[blocked]) - (
                            len(need_to_remove) / CAPACITY_AND_VALUES[blocked][
                        0]))  # update the blocked shift after removing the workers
                    for worker in need_to_remove:
                        if worker in shifts_dict[blocked]:
                            shifts_dict[blocked].remove(worker)
                    # print("workers on {} shift after removal: {}".format(blocked, shifts_dict[blocked]))
            for worker in shifts_dict[shift_name]:  # eventually update assigners salary
                worker_salary_dict[worker] += CAPACITY_AND_VALUES[shift_name][1]
        else:
            blocked_shifts_sorted = []
            for blocked in blocked_shifts:
                blocking_workers = shifts_dict[blocked]
                blocked_shifts_sorted.append(
                    (blocked, len(set(workers).intersection(blocking_workers)), blocking_workers))
            blocked_shifts_sorted = sorted(blocked_shifts_sorted, key=lambda tup: tup[1])
            # print(f"blocked shifts:\n{blocked_shifts}\nSorted:\n{blocked_shifts_sorted}")
            if blocked_shifts_sorted:  # list of trios sorted by y (x,y,z)| x = shift time ; y = num of intersection; z = list of blocking workers
                assign = list(set(workers).difference(
                    shifts_dict[blocked_shifts_sorted[0][0]]))  # the list of workers that not appears as blocked
                if len(assign) < CAPACITY_AND_VALUES[shift_name][0]:  # if they are not enough
                    difference = CAPACITY_AND_VALUES[shift_name][0] - len(
                        assign)  # difference = num of workers we need to add
                    intersection_workers = list(
                        set(workers).intersection(blocked_shifts_sorted[0][2]))  # available to work but blocked
                    intersection_heap = []
                    for worker in intersection_workers:
                        heapq.heappush(intersection_heap, (worker_salary_dict[worker], worker))
                    additional_assign = heapq.nsmallest(difference,
                                                        intersection_heap)  # take the n smallest salaries while n is defference
                    for val, key in additional_assign:
                        assign.append(key)
                    shifts_dict[shift_name] = assign
                    for blocked in blocked_shifts_sorted:
                        shifts_dict[blocked[0]] = list(set(shifts_dict[blocked[0]]).difference(assign))
                        new_len = len(shifts_dict[blocked[0]])
                        heaputil.remove_task(blocked[0])
                        heaputil.add_task(blocked[0],
                                          new_len / CAPACITY_AND_VALUES[blocked[0]][0])
                    for worker in assign:
                        worker_salary_dict[worker] += CAPACITY_AND_VALUES[shift_name][1]
                else:
                    num_to_assign = CAPACITY_AND_VALUES[shift_name][0]
                    assign_heap = []
                    for worker in assign:
                        heapq.heappush(assign_heap, (worker_salary_dict[worker], worker))
                    assign = heapq.nsmallest(num_to_assign, assign_heap)
                    assign_names = []
                    for tup in assign:
                        assign_names.append(tup[1])
                    shifts_dict[shift_name] = assign_names
                    for blocked in blocked_shifts_sorted:
                        shifts_dict[blocked[0]] = list(set(shifts_dict[blocked[0]]).difference(assign_names))
                        new_len = len(shifts_dict[blocked[0]])
                        heaputil.remove_task(blocked[0])
                        heaputil.add_task(blocked[0], (
                                new_len / CAPACITY_AND_VALUES[blocked[0]][0]))
                    for value, worker in assign:
                        worker_salary_dict[worker] += CAPACITY_AND_VALUES[shift_name][1]
            else:
                assign = list(set(workers))
                num_to_assign = CAPACITY_AND_VALUES[shift_name][0]
                assign_heap = []
                for worker in assign:
                    heapq.heappush(assign_heap, (worker_salary_dict[worker], worker))
                assign = heapq.nsmallest(num_to_assign, assign_heap)
                assign_names = []
                for tup in assign:
                    assign_names.append(tup[1])
                shifts_dict[shift_name] = assign_names
                for value, worker in assign:
                    worker_salary_dict[worker] += CAPACITY_AND_VALUES[shift_name][1]

    return shifts_dict


def update_to_selected(values):
    values = values.replace("\'", "\"")
    shifts_dict = json.loads(values)
    next_sunday = get_next_sunday_date()
    for i in range(7):
        week_date = next_sunday + datetime.timedelta(i)
        for j in range(3):
            for worker in shifts_dict[WEEK_DAYS[i] + "_" + SHIFT_OPTIONS[j]]:
                Shift.objects.filter(date=week_date, shift_time=SHIFT_OPTIONS[j], user__username=worker).update(
                    selected=True)


def get_week_schedule(sunday):
    result = {}
    for i in range(7):
        week_date = sunday + datetime.timedelta(i)
        for j in range(3):
            result["{}_{}".format(WEEK_DAYS[i], SHIFT_OPTIONS[j])] = Shift.objects.filter(date=week_date,
                                                                                          shift_time=SHIFT_OPTIONS[
                                                                                              j],
                                                                                          selected=True).values_list(
                'user_id', flat=True)
    for key, value in result.items():
        users_list = []
        for i in range(len(value)):
            users_list.append(User.objects.get(id=value[i]).username)
        result[key] = users_list

    return result


def get_user_shifts(user: User):
    last_sunday = get_next_sunday_date() - datetime.timedelta(7)
    last_saturday = last_sunday + datetime.timedelta(6)
    shifts_list = Shift.objects.filter(date__gte=last_sunday, date__lte=last_saturday, user=user, selected=True)
    print(shifts_list)
    return shifts_list
