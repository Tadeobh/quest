from flask import current_app, g
from pymongo.read_preferences import ReadPreference
from werkzeug.local import LocalProxy
from werkzeug.security import generate_password_hash

from pymongo import MongoClient
from pymongo.read_concern import ReadConcern
from pymongo.write_concern import WriteConcern
from pymongo.results import DeleteResult
from bson.objectid import ObjectId


def get_db():
    """
    Configuration method to return db instance
    """

    # If a database connection object has been already created, 
    # retrieve it from the global variable "g".
    db = getattr(g, "_database", None)

    # Get the database URI from the config object.
    QUEST_DB_URI = current_app.config["QUEST_DB_URI"]

    # Get the database name from the config object
    # and store it in the global variable "g" for later.
    g._db_name = current_app.config["QUEST_DB_NAME"]

    # If there's not an existing connection to the database,
    # create one with the configuration parameters.
    if db is None:

        db = g._database = MongoClient(
            QUEST_DB_URI,
            tls=True,
            tlsAllowInvalidCertificates=True
        )

    # Return the connection to the database.
    return db


def get_db_name():
    
    return current_app.config["QUEST_DB_NAME"]

# Use LocalProxy to get the global db instance with just 'db'.
db = LocalProxy(get_db)

# Use LocalProxy to get the database name with just 'db_name'.
db_name = LocalProxy(get_db_name)

# USER MANAGEMENT
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
    return db[g._db_name].users.insert_one(new_user)


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

    QUEST_DB_NAME = str(db_name)

    # Look for the user with the given email and/or username.
    user = db[QUEST_DB_NAME].users.find_one(query)

    # Return the user that was found.
    return user


# QUESTIONNAIRE MANAGEMENT
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
    return db[g._db_name].questionnaires.insert_one(new_quest)


def get_questionnaire(questner_id):
    """
    Function to get a Questionnaire from the database with its given ID.
    """

    # Pipeline used to get the information about the Questionnaire and the elements
    # linked to it.
    pipeline = [
        {
            '$match': {
                '_id': ObjectId(questner_id)
            }
        }, {
            '$lookup': {
                'from': 'questions', 
                'let': {
                    'questner_id': '$_id'
                }, 
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$questionnaire_id', '$$questner_id'
                                ]
                            }
                        }
                    }, {
                        '$lookup': {
                            'from': 'answers', 
                            'let': {
                                'quest_id': '$_id'
                            }, 
                            'pipeline': [
                                {
                                    '$match': {
                                        '$expr': {
                                            '$eq': [
                                                '$question_id', '$$quest_id'
                                            ]
                                        }
                                    }
                                }
                            ], 
                            'as': 'answers'
                        }
                    }
                ], 
                'as': 'questions'
            }
        }
    ]

    # Process the pipeline
    questionnaire = list(db[g._db_name].questionnaires.aggregate(pipeline))

    # If we have a result, return it.
    # If not, return None.
    if len(questionnaire) > 0:
        return questionnaire[0]
    return None


def delete_questionnaire(questner_id):
    """
    Function to delete a Questionnaire from the database with the given ID.

    It first confirms that the Questionnaire with the given ID exists, and that
    the user sending the request is the owner of the Questionnaire.

    Then, it delets the Questionnaire and the Questions and Answers linked to it.
    """

    # Pipeline to get the information from the Questionnaire that will be deleted,
    # including the IDs from the Questions and Answers linked to it.
    pipeline = [
        {
            '$match': {
                '_id': ObjectId(questner_id)
            }
        }, {
            '$lookup': {
                'from': 'questions', 
                'let': {
                    'questner_id': '$_id'
                }, 
                'pipeline': [
                    {
                        '$match': {
                            '$expr': {
                                '$eq': [
                                    '$questionnaire_id', '$$questner_id'
                                ]
                            }
                        }
                    }, {
                        '$lookup': {
                            'from': 'answers', 
                            'let': {
                                'quest_id': '$_id'
                            }, 
                            'pipeline': [
                                {
                                    '$match': {
                                        '$expr': {
                                            '$eq': [
                                                '$question_id', '$$quest_id'
                                            ]
                                        }
                                    }
                                }, {
                                    '$project': {
                                        '_id': 1
                                    }
                                }
                            ], 
                            'as': 'answers'
                        }
                    }, {
                        '$project': {
                            'answers': 1
                        }
                    }
                ], 
                'as': 'questions'
            }
        }
    ]

    # Process the pipeline and get the result with the information requested.
    questionnaire = list(db[g._db_name].questionnaires.aggregate(pipeline))[0]

    # Confirm that the requester is the owner of the Questionnaire.
    # If not, return None.
    if questionnaire.get('user_id', None) == g._current_user.get('username'):

        # Intialize the variables that will be used to store the elements
        # linked to the Questionnaire.
        questions = list()
        answers = list()

        # Get the list of Questions and Answers linked to the Questionnaire and store their IDs.
        for question in questionnaire.get('questions'):
            question_id = question.get('_id', None)
            if question_id is not None:
                questions.append(question_id)
                answers.extend([answer.get('_id') for answer in question.get('answers') if answer is not None])
        

        # Callback function to execute the operations that will delete the elements.
        def callback(session):

            # Retrieve the collections that will be modified, through the given session.
            questner_coll = session.client.test_quest.questionnaires
            quest_coll = session.client.test_quest.questions
            answer_coll = session.client.test_quest.answers

            # Delete operations
            answer_coll.delete_many({'_id': {'$in': answers}}, session=session)
            quest_coll.delete_many({'_id': {'$in': questions}}, session=session)
            print('Questner ID: ', questner_id)
            questner_coll.delete_one({'_id': ObjectId(questner_id)}, session=session)

        # Start a client session and execute the operations
        with db.start_session() as session:
            session.with_transaction(
                callback,
                read_concern=ReadConcern('snapshot'),
                write_concern=WriteConcern("majority", wtimeout=1000),
                read_preference=ReadPreference.PRIMARY
            )
        
        return {'message': 'Questionnaire deleted!'}

    else:
        return None

# QUESTION MANAGEMENT
def create_question(questionnaire_id, text, type, options=None):
    """
    Function to create a new question and save it to the database.

    It first checks if a questionnaire with the given 'questionnaire_id' exists.
    If it doesn't exists, it will return an error.
    """

    # Check if the questionnaire with the given 'questionnaire_id' exists.
    questionnaire = db[g._db_name].questionnaires.find_one({'_id': ObjectId(questionnaire_id)})

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
        return db[g._db_name].questions.insert_one(new_question)
    
    return {'message': "Could't find questionnaire with the given Questionnaire ID: {}.".format(questionnaire_id)}


def get_question(question_id):
    """
    Function to get a Question from the database with its given ID.
    """

    # Pipeline used to get the information about the Question and the answers
    # linked to it.
    pipeline = [
        {
            '$match': {
                '_id': ObjectId('61b9584a4dbee41f9fc90e1f')
            }
        }, {
            '$lookup': {
                'from': 'answers', 
                'localField': '_id', 
                'foreignField': 'question_id', 
                'as': 'answers'
            }
        }
    ]

    # Process the pipeline and get the result
    question = list(db[g._db_name].questions.aggregate(pipeline))

    # If we have a result, return it.
    # If not, return None.
    if len(question) > 0:
        return question[0]
    return None


def delete_question(question_id):
    """
    Function to delete a Question from the database with its given ID.

    The process is:

    1. Check if the Question with the given ID exists.
    2. If it exists, it checks if the Questionnaire to which the Question is linked belongs to the current user.
    3. If it does, it sends the command to the database to delete the Question.
    """

    # Pipeline to get the information about the Questionnaire to which this Question is linked to.
    pipeline = [
        {
            '$match': {
                '_id': ObjectId(question_id)
            }
        }, {
            '$lookup': {
                'from': 'questionnaires', 
                'localField': 'questionnaire_id', 
                'foreignField': '_id', 
                'as': 'questionnaire'
            }
        }, {
            '$project': {
                '_id': 0, 
                'questionnaire': 1
            }
        }
    ]

    # Run the pipeline and get the result.
    result = db[g._db_name].questions.aggregate(pipeline)

    # Get the owner of the Questionnaire.
    questionnaire_owner = list(result)[0].get('questionnaire')[0].get('user_id')

    # If the current user is the owner of the Questionnaire,
    # delete the Question as requested.
    # If not, return a DeleteResult object with "acknowledged" as False.
    if questionnaire_owner == g._current_user.get("username"):
        return db[g._db_name].questions.delete_one({'_id': ObjectId(question_id)})
    else:
        return DeleteResult(None, False)


# ANSWER MANAGEMENT
def create_answer(question_id, value):
    """
    Function to create a new answer and save it to the database.

    It first checks if a question with the given 'question_id' exists.
    If it doesn't exists, it will return an error.
    """

    # Check if the question with the given 'question_id' exists.
    question = db[g._db_name].questions.find_one({'_id': ObjectId(question_id)})

    if question is not None:

        # Build the new answer that will be added to the database.
        new_answer = {
            'question_id': ObjectId(question_id),
            'value': value
        }

        # Save the new answer in the database and return the result.
        return db[g._db_name].answers.insert_one(new_answer)
    
    return {'message': "Could't find question with the given Question ID: {}.".format(question_id)}


def get_answer(answer_id):
    """
    Function to get an Answer from the database with its given ID.
    """

    # Return Answer with the given Answer ID (answer_id).
    return db[g._db_name].answers.find_one(ObjectId(answer_id))


def delete_answer(answer_id):
    """
    Function to delete an Answer from the database with is given ID.

    It first confirms that the Answer exists and that it is linked to a Questionnaire that belongs to the user.
    """

    # Pipeline to get the information about the Questionnaire to which this Answer is linked to.
    pipeline = [
        {
            '$match': {
                '_id': ObjectId(answer_id)
            }
        }, {
            '$lookup': {
                'from': 'questions', 
                'localField': 'question_id', 
                'foreignField': '_id', 
                'as': 'question'
            }
        }, {
            '$lookup': {
                'from': 'questionnaires', 
                'localField': 'question.0.questionnaire_id', 
                'foreignField': '_id', 
                'as': 'questionnaire'
            }
        }, {
            '$project': {
                '_id': 0, 
                'questionnaire': 1
            }
        }
    ]

    # Run the pipeline and get the result.
    result = db[g._db_name].answers.aggregate(pipeline)

    # Get the owner of the Questionnaire.
    questionnaire_owner = list(result)[0].get('questionnaire')[0].get('user_id')

    print(f"[Delete Answer] Questionnaire owner: {questionnaire_owner} / Current User: {g._current_user.get('username')}")

    # If the current user is the owner of the Questionnaire,
    # delete the Answer as requested.
    # If not, return a DeleteResult object with "acknowledged" as False.
    if questionnaire_owner == g._current_user.get("username"):
        return db[g._db_name].answers.delete_one({'_id': ObjectId(answer_id)})
    else:
        return DeleteResult(None, False)