# HotTopics - social media web-app
I built this app by myself as my Final Project for Harvard's CS50. HotTopic's is a social media app that lets users create posts with up to 4 choices and then like, comment and vote on other posts. You can stay connected by following other users to track the posts they make. My idea for this app was to create a site for people to share their thoughts and have others vote and comment, in other words, a place for people to guage opinions and debate.

## Video Demo
As part of my submission to CS50, I've created a video going over the main functions of the app [here](https://youtu.be/9_j-9qrXA8M).

# Technologies Used
- Python - version 3.10.2
- Flask - version 2.0.1
- jQuery - version 3.6.0
- Flask-SQLAlchemy - version 2.5.1
- PostreSQL Database
- Deployed App to Heroku
- HTML/CSS

# What I Learned
- Got comfortable with Flask microframework which included managing User-Authentication, creating forms and processing GET/POST requests.
- Used jQuery to dynamically load data from back-end using AJAX and JSON. Also made traversing DOM and selecting elements easy.
- SQLalchemy allowed me to create models to represent data for users and posts. This made querying my PostgreSQL database simpler by using the relational models.
- Creating custom, responsive styles using CSS and HTML. 
- This project allowed me to explore a lot of new technologies that I had never used before. I learned how to research and teach myself new subjects by watching online tutorials, searching for answers in code forums like Stack Overflow, and even reading documentation.
- Organizing, managing and executing a large scale project from start to finish

# Features
- User authentication system that stores salted hashed passwords in the database. Used Flask LoginManager to log in and log out users to keep track of current users
- Used flask_wtf to create forms that validate user input to make it easier to process requests in the backend
- The Home Page has infinite scrolling, so that before users reach the bottom of page, the front end sends an AJAX request for more posts to be displayed
- Recommended accounts are displayed in the sidebar based of the number of common friends and the number of followers the recommended account has
- You're able to choose pictures from file system for custom profile pictures
- While in the Profile Page, you can choose to edit your name/email and change your password
- Search Page that gives you real-time search results for posts and usernames.
- Responsive site is designed for both mobile and desktop devices using media-queries. Includes sidebar that resizes based on the size of the screen and is opened and closed by swiping on mobile

# Status - Complete
My app is finished and is deployed to Heroku. Visit the site using this [link](https://hottopics1.herokuapp.com/).

# Acknowledgements
I created my Flask back-end by following Corey Schafer's ["Python Flask Tutorial: Full-Featured Web App"](https://www.youtube.com/watch?v=MwZwr5Tvyxo&list=PL-osiE80TeTs4UjLw5MM6OjgkjFeUxCYH). This tutorial covered topics such as user-authentication, setting up a database, creating forms and implementing the package structure to a project.
