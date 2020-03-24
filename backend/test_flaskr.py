import os
import unittest
import json
from flask_sqlalchemy import SQLAlchemy
from flask_cors import CORS


from flaskr import create_app
from models import setup_db, Question, Category


class TriviaTestCase(unittest.TestCase):
    """This class represents the trivia test case"""

    def setUp(self):
        """Define test variables and initialize app."""
        self.app = create_app()
        self.client = self.app.test_client
        self.database_name = "trivia_test"
        self.database_path = "postgres://{}/{}".format('localhost:5432', self.database_name)
        setup_db(self.app, self.database_path)


        self.new_question = {
            'question': 'What is the capital of Georgia, USA?',
            'answer': 'Atlanta',
            'difficulty': 1,
            'category': '3'
        }
        # binds the app to the current context
        with self.app.app_context():
            self.db = SQLAlchemy()
            self.db.init_app(self.app)
            # create all tables
            self.db.create_all()
    
    def tearDown(self):
        """Executed after reach test"""
        pass

    """
    TODO
    Write at least one test for each test for successful operation and for expected errors.
    """
    def test_get_categories(self):
        res = self.client().get('/categories')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['categories'])

    def test_404_if_get_categories_failed(self):
        res = self.client().get('/categories/1000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_get_questions(self):
        res = self.client().get('/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(len(data['questions']))
        self.assertTrue(data['categories'])
        self.assertTrue(data['total_questions'])

    def test_404_sent_requesting_beyond_valid_page(self):
        res = self.client().get('/questions?page=2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_delete_question(self):
        res = self.client().delete('/questions/90')
        data = json.loads(res.data)

        question = Question.query.filter(Question.id == 90).one_or_none()

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(data['deleted'], 90)
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
        self.assertEqual(question, None)

    def test_404_if_question_is_none(self):
        res = self.client().delete('/questions/2000')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'unprocessable')

    def test_create_question(self):
        res = self.client().post('/questions', json=self.new_question)
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['created'])
        self.assertTrue(data['total_questions'])
        self.assertTrue(len(data['questions']))
    
    def test_422_if_question_creation_failed(self):
        old_num_questions = len(Question.query.all())
        res = self.client().post('/questions', json={})
        data = json.loads(res.data)
        
        new_num_questions = len(Question.query.all())

        self.assertEqual(res.status_code, 422)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], "unprocessable")
        self.assertTrue(old_num_questions == new_num_questions)

    def test_search_questions(self):
        res = self.client().post('/questions/search', json={'searchTerm':'World Cup'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 2)
        self.assertEqual(data['questions'][0]['id'], 10)
        self.assertEqual(data['questions'][1]['id'], 11)

    def test_404_if_search_questions_failed(self):
        res = self.client().post('/questions/search', json={'searchTerm': 'xxxhuhuhuhu'})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_get_question_by_category(self):
        res = self.client().get('categories/5/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertEqual(len(data['questions']), 4)
        self.assertEqual(data['current_category'], 5)

    def test_404_if_questions_by_category_fails(self):
        res = self.client().get('/categories/1000/questions')
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 404)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'Not found')

    def test_play_quiz(self):
        res = self.client().post('/quizzes', json={'previous_questions':[10,11],
                                            'quiz_category': {'type': 'Science', 'id': '1'}})
        data = json.loads(res.data)  

        self.assertEqual(res.status_code, 200)
        self.assertEqual(data['success'], True)
        self.assertTrue(data['question']) 
        self.assertTrue(data['question']['category'], 1)
        self.assertNotEqual(data['question']['id'], 10) 
        self.assertNotEqual(data['question']['id'], 11)
    
    def test_play_quiz_failed(self):
        res = self.client().post('/quizzes', json={})
        data = json.loads(res.data)

        self.assertEqual(res.status_code, 400)
        self.assertEqual(data['success'], False)
        self.assertEqual(data['message'], 'bad request')

# Make the tests conveniently executable
if __name__ == "__main__":
    unittest.main()