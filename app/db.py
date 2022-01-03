from flask import current_app, g
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash

from pymongo import MongoClient
from bson.objectid import ObjectId

def get_db():
    """
    Configuration method to return db instance
    """

    # If a database connection object has been already created, 
    # retrieve that from the global variable "g".
    db = getattr(g, "_database", None)

    # Get the configuration parameters for the database from the
    # config object.
    QUEST_DB_URI = current_app.config["QUEST_DB_URI"]
    QUEST_DB_NAME = current_app.config["QUEST_DB_NAME"]

    # If there's not an existing connection to the database,
    # create one with the configuration parameters.
    if db is None:

        db = g._database = MongoClient(
            QUEST_DB_URI,
            tls=True,
            tlsAllowInvalidCertificates=True
        )[QUEST_DB_NAME]

    # Return the connection to the database.
    return db
    

# Use LocalProxy to read the global db instance with just `db`.
db = LocalProxy(get_db)


def get_user(email=None, username=None) -> dict:
    """
    Function to return from the database the user with the
    given 'email' or 'username'.

    If both parameters are given, the function will look for
    a user that 'matches' both email and 'username' args.
    """

    # Build the query 'query' to be sent to the database.
    query = {
    '$and': 
        [
            {'email': email if email is not None else {'$exists': True}},
            {'username': username if username is not None else {'$exists': True}}
        ]
    }

    print("[get_user] Searching for: ", query)

    # Look for the user with the given email and/or username.
    user = db.users.find_one(query)

    print("[get_user] User found: ", user)

    # Return the user that was found.
    return user


def create_new_user(email, username, password):
    """
    Function to create a new user and save it to the database.
    """

    # Build the new user to be added to the databse.
    new_user = {
        'username': username,
        'email': email,
        'password': generate_password_hash(password),
    }

    print("[create_new_user] Creating new user: ", new_user)

    # Save the new user in the database and return the result.
    return db.users.insert_one(new_user)


def create_questionnaire(title, user_id):
    """
    Function to create a new questionnaire and save it to the database.
    """

    # Build the new questionnaire that will be added to the database.
    new_quest = {
        'title': title,
        'user_id': user_id,
    }

    print(f'[Create_Quest] Questionnaire to create: title={title}, user_id={user_id}')

    # Save the new questionnaire in the database and return the result.
    return db.questionnaires.insert_one(new_quest)


def get_questionnaire(questner_id):
    """
    Function to get a Questionnaire from the database with its given ID.
    """

    # Return Questionnaire with the given Questionnaire ID (questner_id).
    return db.questionnaires.find_one(ObjectId(questner_id))


def create_question(questionnaire_id, text, type, options=None):
    """
    Function to create a new question and save it to the database.

    It first checks if a questionnaire with the given 'questionnaire_id' exists.
    If it doesn't exists, it will return an error.
    """

    # Check if the questionnaire with the given 'questionnaire_id' exists.
    questionnaire = db.questionnaires.find_one({'_id': ObjectId(questionnaire_id)})

    if questionnaire is not None:

        # Build the new question that will be added to the database.
        new_question = {
            'questionnaire_id': ObjectId(questionnaire_id),
            'text': text,
            'type': type
        }

        # If there are options, add them to the question.
        if options is not None:
            new_question['options'] = options

        # Save the new question in the database and return the result.
        return db.questions.insert_one(new_question)
    
    return {'message': "Could't find questionnaire with the given Questionnaire ID: {}.".format(questionnaire_id)}


def get_question(question_id):
    """
    Function to get a Question from the database with its given ID.
    """

    # Return Question with the given Question ID (question_id).
    return db.questions.find_one(ObjectId(question_id))


def get_answer(answer_id):
    """
    Function to get an Answer from the database with its given ID.
    """

    # Return Answer with the given Answer ID (answer_id).
    return db.answers.find_one(ObjectId(answer_id))


def create_answer(question_id, value):
    """
    Function to create a new answer and save it to the database.

    It first checks if a question with the given 'question_id' exists.
    If it doesn't exists, it will return an error.
    """

    # Check if the question with the given 'question_id' exists.
    question = db.questions.find_one({'_id': ObjectId(question_id)})

    if question is not None:

        # Build the new answer that will be added to the database.
        new_answer = {
            'question_id': ObjectId(question_id),
            'value': value
        }

        # Save the new answer in the database and return the result.
        return db.answers.insert_one(new_answer)
    
    return {'message': "Could't find question with the given Question ID: {}.".format(question_id)}