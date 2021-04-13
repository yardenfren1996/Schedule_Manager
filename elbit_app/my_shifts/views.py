
from django.shortcuts import render
from django.http import HttpResponseRedirect, HttpResponse
from django.urls import reverse
from django.contrib.auth import authenticate, login, logout
from django.contrib.auth.decorators import login_required
from . import utils

import datetime

from .forms import WorkerForm, WorkerProfileInfoForm



# functions

def home(request):
    # utils.make_fake_shifts_for_test()
    if request.user.is_anonymous:
        user_shifts = []
    else:
        user_shifts = utils.get_user_shifts(request.user)
    return render(request, 'home.html', {'user_shifts': user_shifts})


@login_required
def user_logout(request):
    logout(request)
    return HttpResponseRedirect(reverse('home'))


def register(request):
    registered = False

    if request.method == 'POST':
        user_form = WorkerForm(data=request.POST)
        additional_detail_form = WorkerProfileInfoForm(data=request.POST)

        if user_form.is_valid() and additional_detail_form.is_valid():

            user = user_form.save()
            user.set_password(user.password)
            user.save()

            profile = additional_detail_form.save(commit=False)
            profile.worker = user
            profile.save()

            registered = True

        else:
            print(user_form.errors)
    else:
        user_form = WorkerForm()
        additional_detail_form = WorkerProfileInfoForm()

    return render(request, 'registration.html',
                  {'user_form': user_form, 'additional_detail_form': additional_detail_form, 'registered': registered})


def user_login(request):
    if request.method == 'POST':
        username = request.POST.get('username')
        password = request.POST.get('password')

        user = authenticate(username=username, password=password)

        if user:
            if user.is_active:
                login(request, user)
                return HttpResponseRedirect(reverse('home'))
            else:
                return HttpResponse("ACCOUNT NOT ACTIVE")
        else:
            print("Someone try to login and failed")
            print("Username: {} and password {} ".format(username, password))
            return HttpResponse("Invalid login details supplied")
    else:
        return render(request, 'login.html', {})


@login_required
def submitting_shifts(request):
    next_sunday = utils.get_next_sunday_date()
    next_week_dates = []
    for i in range(7):
        next_week_dates.append((next_sunday + datetime.timedelta(i)).__str__())
    return render(request, 'shifts_to_send.html',
                  {'next_week_dates': next_week_dates, 'shift_options_list': utils.SHIFT_OPTIONS, })


@login_required
def send_confirm(request):
    if request.method == 'POST':
        values = request.POST.getlist('result')[0]
        utils.delete_previous_shifts(request.user)
        utils.create_shifts(values, request.user)
    return render(request, 'send_confirm.html', {})


@login_required
def create_schedule(request):
    shifts_dict = utils.get_list_of_workers_per_day()
    return render(request, 'create_schedule.html',
                  {'shifts_dict': shifts_dict,
                   'total_shifts_mat': utils.TOTAL_SHIFTS_MAT,
                   'capacity_dict': utils.CAPACITY_AND_VALUES})


@login_required
def approve_schedule(request):
    shifts_dict = utils.make_schedule()
    if request.method == 'POST':
        return HttpResponseRedirect('post_schedule')
    return render(request, 'approve_schedule.html',
                  {'shifts_dict': shifts_dict,
                   'total_shifts_mat': utils.TOTAL_SHIFTS_MAT,
                   'capacity_dict': utils.CAPACITY_AND_VALUES})


@login_required
def post_schedule(request):
    values = request.POST.getlist('result')[0]
    utils.update_to_selected(values)
    return render(request, 'post_schedule.html', {})


@login_required
def work_schedule(request):
    next_week = utils.get_next_week_dates(utils.get_next_sunday_date())
    last_week = utils.get_next_week_dates(next_week[0] - datetime.timedelta(7))
    current_schedule = utils.get_week_schedule(last_week[0])
    next_schedule = utils.get_week_schedule(next_week[0])
    return render(request, 'this_week_shifts.html',
                  {'current_schedule': current_schedule, 'next_schedule': next_schedule,
                   'total_shifts_mat': utils.TOTAL_SHIFTS_MAT, 'next_week': next_week, 'last_week': last_week,
                   'week_days': utils.WEEK_DAYS, 'range7': range(7)}
                  )
