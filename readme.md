# CS50 - Final Project - Tech Recycle for Education

Hello, my name is Diego, I’m 37 years old, I’m from Brazil and I live in the State of São Paulo. I’m a teacher at a school, and it was thinking about the school that I came up with the idea for the final CS50 project.

We have a project to create an electronics, computer and robotics laboratory at the school, but we have no resources or equipment. We started with small classes teaching programming with Arduino but we had limited resources because the teachers donated all material.

My idea was to create a website that makes it possible to donate electronic equipment to schools that want to create a laboratory to teach programming and electronics. That way schools could register and people could donate smartphones, computers, laptops that they no longer use.

My project Tech Recycle for Education was developed with a focus on two types of users, Donors, that could have some spare gadget getting dust at home and Schools that could use these gadgets to build a maker lab to teach programming.



## Website features

**Donors can:**

- Register on the website

- Login

- Access the map that shows all registered schools

- Select a school and see its details

- Donate something the school needs

- Change your password

- View your donation history

- View your ranking position

- Log out

  

**Schools can:**

- Login

- View the history of donations received

- Mark a donation as received

- Log out

  

**The Administrator can:**

- Register a new school

- Change the registration of an existing school

- Remove a school

  

When a donation is made, the donor only receives points after the school confirms receipt of the equipment. The ranking is created only with points of donations received.



## Tables used in the project

**schools**
id, name, address, city, state, country, phone, email, password, latitude, longitude, photo
Stores information about schools.

**users**
id, name, email, password, photo
Saves user data

**items**
id, name, description, icon, scores
It contains all the items that schools can order, along with the score for each item.

**school_items**
id, school_id, item_id
Lists the items that each school wants to receive.

**Donations table**
id, user_id, school_id, item_id, amount, received
Lists the donations of each user for each school and whether the donation was received.



## Technologies used

The site was built using Flask (Python), SQLite3 for the database, CSS preprocessor (SASS) and javascript. I made the codes to upload photos after change the image name, hash all passwords, an administration page that permits add, remove and update schools, used advanced SQL queries to calculate users points, and much more.



## Conclusion

It was very interesting to create this project from scratch using Flask and I used a lot of new resources for me, which I had never worked with before. I spent a lot of time studying and testing before implementing the code. All references to the pages I used as a support are commented on in the code. 

I learned a lot from this project, and I was very happy with the result.