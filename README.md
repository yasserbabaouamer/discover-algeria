## 1. DiscoverAlgeria

DiscoverAlgeria: Your Gateway to the Wonders of Algeria

## 2. Project description:

DiscoverAlgeria is a comprehensive tourism platform designed to showcase the beauty and attractions of Algeria. It aims to provide travelers with detailed information about various tourist destinations, cultural experiences, accommodation options, guided tours, and helpful tips to enrich their exploration of Algeria.

## 3. Table of contents

- [Features](#4-features)
- [Installation](#5-basic-installation-guide)
- [Technologies used](#6-technologies-used)
- [Screenshots](#7-screenshots)
- [Reflection](#8-reflection)
- [Project Status](#8-project-status)
- [Acknowledgements](#9-acknowledgements)
- [Contact](#10-contact-information)

## 4. Features

- **Register a new account**
- **Search for destinations, hotels, tours, or touristic agencies**
- **View details of destinations, hotels, and tours**
- **Browse hotels and activities available in a city**
- **Check room availability within a specified date range at a specific hotel**
- **Filter search results based on various criteria (e.g., amenities, price range)**
- **View available room types in a hotel**
- **Log in and log out of their account**
- **View and manage profile information (statistics, update profile, delete account)**
- **Reset password**
- **Select and reserve rooms, and make payments for reservations**
- **Add reviews for hotels post-reservation**
- **View past reservations**
- **Manage favorites and personal reviews**
- **View monthly and yearly statistics**
- **View, add, update, and delete hotel information**
- **Manage hotel and room cancellation policies, prepayment policies, and parking arrangements**
- **Manage room reservations (view and cancel)**
- **View room statistics**
- **Add, update, and delete room types**
- **View, update, and delete guest and owner accounts**
- **Automatically assign available rooms to confirmed reservations**
- **Automatically Update Reservation Status Periodically**
- **Ensure secure and efficient payment processing for reservations (via Stripe)**

## 5. Basic Installation Guide

### Prerequisites:

- Python v3.11
- Node.js v16.20.2
- npm 8.19.4
- Git

1. Clone the repository to your local machine:

    ```bash
    git clone https://github.com/yasserbabaouamer/discover-algeria.git
    ```

1. Navigate the project directory, and create a virtual environement
    
    ```bash
    virtualenv -p python3 venv
    ```
    
2. Activate the virtual environment
    
    On Linux
    
    ```bash
    source venv/bin/activate
    ```
    
    On windows
    
    ```bash
    venv\Scripts\activate
    ```
    

1. Install the project requirements
    
    ```bash
    pip install -r requirements.txt
    ```
    

1. Open the project in your preferred IDE and configure it to use the interpreter from the virtual environment.

## 6. Technologies used:

- Frontend: React, HTML, CSS, JavaScript
- Backend: Django, DRF
- Databases: MariaDB
- Task sheduling: celery, celery-beats, redis
- Authentication: JWT
- API documentation: OpenAPI (drf-spectacular)

## 7. Screenshots

![home-screen](https://github.com/user-attachments/assets/4d3ee308-beb6-43bf-ac93-f2418f7c61a9)
 :--:
 figure 1: home screen

![login-screen](https://github.com/user-attachments/assets/9932fcb4-6736-42b0-888b-75d2ebefd9f7)
:--:
 figure 2: login screen
 
![checkout](https://drive.usercontent.google.com/download?id=1zKu07q7vMbcMh1woOAfJddRr9RfRmGVg)
:--:
 figure 3: checkout page

 more screenshots
 <br><br>
<img alt="admin_guests" src="https://github.com/user-attachments/assets/b4ee2814-97e7-4cfa-81da-9e252d9e3496" width="30%" style="height: 200px; object-fit: cover;"></img>
<img alt="owner_hotels" src="https://github.com/user-attachments/assets/f0fe2bd6-e1cf-4910-a647-b4b456d3a46f" width="30%" style="height: 200px; object-fit: cover;"></img>
<img alt="hotel details" src="https://github.com/user-attachments/assets/32556b3c-2dd6-4095-a926-b1262109806b" width="30%" style="height: 200px; object-fit: cover;"></img>
<img alt="guest profile" src="https://github.com/user-attachments/assets/9cf911d6-8316-40b9-8da4-26faf785ebe1" width="30%" style="height: 200px; object-fit: cover;"></img>
<img alt="admin_owners" src="https://github.com/user-attachments/assets/d6d02cb0-1727-4703-a9ef-9d31c267475d" width="30%" style="height: 200px; object-fit: cover;"></img>
<img alt="city_hotels" src="https://drive.usercontent.google.com/download?id=1bP7kwflG_B5NQL1Z_6qGq33l1kW54iFL" width="30%" style="height: 200px; object-fit: cover;"></img>


## 8. Reflection

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

I needed a fast and efficient search algorithm with recommendation features. Starting with the Levenshtein algorithm in Python, I found it too slow. I then moved to a PL/SQL implementation, but it still wasn’t fast enough. Finally, I wrote the algorithm in C and used it as a User-Defined Function (UDF) in the database, achieving a dramatic performance boost. The query time improved from 1.1 seconds (PL/SQL) to 0.0009 seconds (C UDF), making it 1222x times faster. tested on a table with over 2100 indexed records.

### Designing an innovative authentication flow

I developed a comprehensive authentication flow that seamlessly integrates the signup, login, account confirmation, and password reset processes. The diagram illustrates this flow in detail.[link](https://drive.google.com/file/d/1y58gcR33Mlc4A6VeoGFvjwr6mwDlYE_3/view?usp=sharing)

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

 ## 8. Project Status
 **Alpha Version**: This project is currently in the alpha version. We are actively working on it and plan to add new features in the future.


 ## 9. Acknowledgements
- Thanks to all the open-source libraries used in this project.
- Special thanks to [brahim bafouloulou](https://github.com/brahimbafou) for collaboration.

## 10. Contact Information

For any inquiries, please contact me at [yacerbaba10@gmail.com].
