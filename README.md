# Overview

This software is an interface for a cloud database that holds information about LLM prompts. It allows CRUD operations on the data stored in the database.

## Using the software

### Setting up
1. Clone this repository
2. Set up the database
    1. Create a Firebase project
    2. Create a Firestore database
    3. Generate a private key under Settings > Service accounts
    4. Rename the downloaded JSON file to `admin-key.json` and put it where the repo is cloned
3. Run `pip install firebase-admin streamlit`
4. Run `setup-data.py` to load data into your database

### Running the interface
1. Run `streamlit run main.py`

I wrote this software to get a better understanding of how cloud NoSQL databases work and could be used.

[Software Demo Video](https://youtu.be/g2F42hj7T3U)

# Cloud Database

I am using Google Firestore as my database.

The database has one 'table' that holds all of the information that is contained in a prompt.

# Development Environment

I used VS Code to develop the software.

The software was written in Python with the streamlit and firestore libraries.

# Useful Websites

- [Firestore Tutorial](https://firebase.google.com/docs/firestore)
- [Firebase Admin SDK setup](https://firebase.google.com/docs/admin/setup#python)
- [Firestore quickstart with server client library](https://docs.cloud.google.com/firestore/native/docs/create-database-server-client-library#python)

# Future Work

- Change hacky setting of `ttftMs` field to `null` to something better
- Add button that auto-populates form given specific id for easy updating
- Visual display of tools list