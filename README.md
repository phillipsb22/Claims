# Claims
Flask and Restplus Mock api using google oAuth

# Setup
Setup your python environment requirements are located in requirements file in main directory
To setup this API run the python script under Tests folder called setup
Register your google service on google console and add the keys to the main app.py file
At the moment the images storage is set to current directory.
The first user that you create will by default be an admin user, any subsequent users will be a general user
Admin users can be both general and admin users at the same time
Special considerations:
    put the full path to the image where it is stored
    you can only upload that image once before you have to remove it from the save location and start again


# Testing
Setup on linux based localhost
open browser and navigate to localhost:5000/login
you will be returned a google access key copy this and use this key as a parameter to execute the test.py script located in Tests Directory
you will need to use a admin user for all the tests to complete successfully
