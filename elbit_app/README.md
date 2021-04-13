Wellcome to my Schedule Manager Project!

in order to start and bee able to see the project please follow the instructions

1. first we want to start the up
    open the terminal in the "elbit_app" project and then run the following command:
    $ python manage.py runserver
    
2. the app is ready. now we need to login in order to be able to see the functionality
    i have created user account for the viewers, enter "Login" on the right corner on the NavBar
    username: "user"
    password: "password"
    and you're in 
    
3. now you can add your shifts on the "Submitting Shifts" tab
 
4. now you can see your shifts adding on the "Create Schedule" tab
 
5. if you want i created fake generator all you need to do is to accsess the views.py file inside my_shifts directory
    look for the first function called "home"
    there is a comment there "# utils.make_fake_shifts_for_test()"
    uncomment it
    press on the logo on the browser
    than comment it again
    
6. now you can go again to "Create Schedule" tab and see the full table of assignments

7. press on "Submit" button on the bottom of the table and you will see that the workers had assigned to their shifts

8. hit "Post" and then youve posted the working schedule you can see it live on the "Work Schedule" tab


    
