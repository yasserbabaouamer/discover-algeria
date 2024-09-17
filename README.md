## DiscoverAlgeria

DiscoverAlgeria: Your Gateway to the Wonders of Algeria

## Project description:

DiscoverAlgeria is a comprehensive tourism platform designed to showcase the beauty and attractions of Algeria. It aims to provide travelers with detailed information about various tourist destinations, cultural experiences, accommodation options, guided tours, and helpful tips to enrich their exploration of Algeria.

## Table of contents

- [Features](#1-features)
- [Technologies used](#2-technologies-used)
- [Screenshots](#3-screenshots)
- [Reflection](#4-reflection)
- [Project Status](#5-project-status)
- [Acknowledgements](#6-acknowledgements)
- [Contact](#7-contact-information)

## 1. Features

**The visitor can:**

- **Search for destinations, hotels, tours, or touristic agencies**
- **Filter search results based on various criteria (e.g., amenities, price range)**
- **View details of destinations, hotels, and tours**
- **Browse hotels and activities available in a city**
- **View hotel or agency owner information**
- **Check room availability for a specific date range at a hotel**
- **View available room types in a hotel**
- **Register a new account**

**The platform user can:**

- **Log in and log out of their account**
- **Reset their password**
- **View and manage profile information (e.g., view statistics, update profile, delete account)**
- **Manage favorites and personal reviews**

**The guest can:**

- **Select and reserve rooms**
- **Make payments for reservations**
- **Leave reviews for hotels after reservations**
- **View past reservations**

**The hotel owner can:**

- **View, add, update, and delete hotel information**
- **Manage hotel policies (e.g., cancellation, prepayment, parking)**
- **View monthly and yearly statistics**
- **Manage room reservations (e.g., view and cancel)**
- **Add, update, and delete room types**
- **View room statistics**

**The tourism agency can:**

- **Manage agency information**
- **View, add, update, and delete tours (to be added soon)**

**The admin can:**

- **Manage guest and owner accounts**

**The system will:**

- **Automatically assign available rooms to confirmed reservations**
- **Automatically update reservation status periodically**
- **Ensure secure and efficient payment processing for reservations (via Stripe)**

## 2. Technologies used

- Frontend: React, HTML, CSS, JavaScript
- Backend: Python, C, Django, DRF
- Databases: MariaDB
- Cloud/Infrastructure: Docker, AWS (EC2 for hosting, S3 for storage)
- Web server: Gunicorn, (Nginx to be added soon)
- Task scheduling: celery, celery-beats, redis
- Authentication: JWT
- API documentation: OpenAPI (drf-spectacular)

## 3. Screenshots

![home-page](https://drive.usercontent.google.com/download?id=1oWjMkzlHpfSyAJGV4mSxapvJ-ge0e-9e)
 :--:
 figure 1: Home page

![hotel-details-page](https://drive.usercontent.google.com/download?id=1RERA8IrJvqllPbCheZjV7zM3CtntXvz0)
:--:
 figure 2: Hotel details page
 

![city-details-page](https://drive.usercontent.google.com/download?id=1yOox2yZhP7sfXrkPn87D3ChxNeYfjx4M)
:--:
 figure 3: City details page

![city-details-page](https://drive.usercontent.google.com/download?id=1I92sk1hWjuQhkblKIGOm-jurNMku0B6i)
:--:
 figure 4: City hotels page

![checkout-page](https://drive.usercontent.google.com/download?id=1I_q0hUGOTTyUOTVvBdUhtgdleJBSWsAR)
:--:
 figure 5: Checkout page

![city-details-page](https://drive.usercontent.google.com/download?id=1szkuoiv6CrdXhvH0prOuDx6pX5g9wEe8)

![city-details-page](https://drive.usercontent.google.com/download?id=17xfms4U9Okq6Ga-8z42TGyDHnL_G7zjf)

![city-details-page](https://drive.usercontent.google.com/download?id=1Q_ceq5B5cb1IyOYr3f8WF-Hsdg9Bizt_)

![city-details-page](https://drive.usercontent.google.com/download?id=1X1sTcLW5bqWA8FwgMeuD0j_QBmRvuwm3)

![city-details-page](https://drive.usercontent.google.com/download?id=1Bgcfsyr5XieOxftuZCQQRxZvQHd_WHYD)
:--:
 figure 6: Edit Hotel information page

![admin-guests](https://drive.usercontent.google.com/download?id=1HfbZ4nhkeP3spTVM23yfFJSmlxFk3gAX)
:--:
 figure 7: Edit Guests -Admin-

![admin-hosts](https://drive.usercontent.google.com/download?id=1Og3eFTRFQQtpFnJsCzURcuzy07mnvZFL)
:--:
 figure 8: Edit Hosts -Admin-


## 4. Reflection

This project was built to obtain a bachelor's degree in software engineering, Project goals was:

- **Showcasing Algerian Cities and Tourist Attractions**
    
    Highlighting Algeria's cities and tourist attractions with detailed information.
    
- **Facilitating Travel Planning for Visitors**
    
    Providing a platform for travelers to find and book hotels, tours, and services.
    
- **Empowering Local Stakeholders**
    
    Enabling local stakeholders, such as accommodation owners and touristic agencies, to contribute and enhance the platform.
    

We chose **Django** for the backend due to its productivity, built-in features, powerful ORM, and extensive libraries, making development efficient and straightforward.

**React** was selected for its reliable code, robust design, component-based architecture, and strong community support, ensuring a smooth and responsive user interface.

## Challenges Faced

### Implementing a Fast Search Algorithm with Recommendations

I needed a fast and efficient search algorithm with recommendation features. Starting with the Levenshtein algorithm in Python, I found it too slow. I then moved to a PL/SQL implementation, but it still wasn’t fast enough. Finally, I wrote the algorithm in C and used it as a User-Defined Function (UDF) in the database, achieving a dramatic performance boost. The query time improved from 1.1 seconds (PL/SQL) to 0.009 seconds (C UDF), making it 122x times faster. tested on a table with over 2100 indexed records.

### Designing an innovative authentication flow

I developed a comprehensive authentication flow that seamlessly integrates the signup, login, account confirmation, and password reset processes. The diagram illustrates this flow in detail. [link](https://drive.google.com/file/d/1y58gcR33Mlc4A6VeoGFvjwr6mwDlYE_3/view?usp=sharing)

**Why I chose this approach:**

- **Unified System**: This flow ensures a consistent authentication experience across the entire platform, eliminating the need to design separate flows for each feature or user type.
- **Simplified Maintenance**: By having a single, unified authentication flow, maintaining and updating the system becomes easier and less error-prone.
- **Security**: A unified flow allows for more robust and centralized security measures, ensuring that all aspects of authentication are handled with the same level of scrutiny and protection.
- **Consistency**: Having a standardized process ensures that all users follow the same steps, making the system more predictable and reliable.
- **Enhanced User Experience**: Users benefit from a streamlined process, reducing confusion and improving their overall experience on the platform.

### Managing Multiple Profiles with the Same Email and Password

I tackled the challenge of allowing users to manage multiple profiles (guest, host, touristic agency owner) with the same email and password.

- **Profile Identification**: Implemented dynamic routing to direct users to the correct profile based on the login endpoint.
- **Data Segregation**: Designed a database schema to logically separate user data while maintaining a single account for login.
- **Role-Specific Permissions**: Integrated a role-based access control system to adjust features based on the user's profile.

### Managing complex queries and filters

The system required numerous complex queries and filters to deliver detailed statistics and results. Initially, I struggled with writing multiple subqueries in Django, as they were hard to manage. That's when I discovered the [django-sql-utils](https://github.com/martsberger/django-sql-utils) package. This package greatly simplified the process, making it easier to write subqueries and handle conditions within them, streamlining the development of complex queries.

 ## 5. Project Status
 **Alpha Version**: This project is currently in the alpha version. We are actively working on it and plan to add new features in the future.


 ## 6. Acknowledgements
- Thanks to all the open-source libraries used in this project.
- Special thanks to [brahim bafouloulou](https://github.com/brahimbafou) for collaboration.

## 7. Contact Information

For any inquiries, please contact me at [yacerbaba10@gmail.com].
