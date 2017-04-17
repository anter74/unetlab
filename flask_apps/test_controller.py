#!/usr/bin/env python3
""" Tests for controller app """
__author__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__copyright__ = 'Andrea Dainese <andrea.dainese@gmail.com>'
__license__ = 'https://creativecommons.org/licenses/by-nc-nd/4.0/legalcode'
__revision__ = '20170403'

from controller import app, api_key
import base64, json, os, random, tempfile, unittest

admin_username = 'admin'
admin_password = 'admin'

role_1 = 'z' + ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for c in range(7))
username_1 = 'z' + ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for c in range(9))
password_1 = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for c in range(20))
password_2 = ''.join(random.choice('0123456789abcdefghijklmnopqrstuvwxyz') for c in range(20))

class FlaskTestCase(unittest.TestCase):
    def setUp(self):
        self.app = app.test_client()

    def test_00_00_auth_via_api(self):
        # curl -s -D- -X GET 'http://127.0.0.1:5000/api/v1/auth?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/auth?api_key={}'.format(api_key)
        response = self.app.get(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data']['email'], 'admin@example.com')
        self.assertEqual(response_data['data']['labels'], -1)
        self.assertEqual(response_data['data']['name'], 'Default Administrator')
        self.assertEqual(response_data['data']['roles'], ['admin'])
        self.assertEqual(response_data['data']['username'], 'admin')

    def test_00_01_auth_via_auth(self):
        # curl -s -D- -u admin:admin -X GET 'http://127.0.0.1:5000/api/v1/auth'
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(str.encode(admin_username) + b':' + str.encode(admin_password)).decode('utf-8'),
        }
        url = '/api/v1/auth?api_key={}'.format(api_key)
        response = self.app.get(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data']['email'], 'admin@example.com')
        self.assertEqual(response_data['data']['labels'], -1)
        self.assertEqual(response_data['data']['name'], 'Default Administrator')
        self.assertEqual(response_data['data']['roles'], ['admin'])
        self.assertEqual(response_data['data']['username'], 'admin')

    """
    Tests about roles
    """

    def test_01_00_get_roles_via_api(self):
        # curl -s -D- -X GET 'http://127.0.0.1:5000/api/v1/roles?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/roles?api_key={}'.format(api_key)
        response = self.app.get(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data']['admin']['can_write'], True)
        self.assertEqual(response_data['data']['admin']['access_to'], '*')

    def test_01_01_post_role_via_api(self):
        # curl -s -D- -X POST -d '{"role":"test1","can_write":true,"access_to":"*"}' -H 'Content-type: application/json' 'http://127.0.0.1:5000/api/v1/roles?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/roles?api_key={}'.format(api_key)
        data = {
            'role': role_1,
            'can_write': False,
            'access_to': '*'
        }
        response = self.app.post(url, data = json.dumps(data), content_type = 'application/json')
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][role_1]['can_write'], False)
        self.assertEqual(response_data['data'][role_1]['access_to'], '*')

    def test_01_02_get_role_via_api(self):
        # curl -s -D- -X GET 'http://127.0.0.1:5000/api/v1/roles/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/roles/{}?api_key={}'.format(role_1, api_key)
        response = self.app.get(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][role_1]['can_write'], False)
        self.assertEqual(response_data['data'][role_1]['access_to'], '*')

    def test_01_03_patch_role_via_api(self):
        # curl -s -D- -X PATCH -d '{"can_write":false,"access_to":"something*"}' -H 'Content-type: application/json' 'http://127.0.0.1:5000/api/v1/roles/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/roles/{}?api_key={}'.format(role_1, api_key)
        data = {
            'can_write': True,
            'access_to': 'something*'
        }
        response = self.app.patch(url, data = json.dumps(data), content_type = 'application/json')
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][role_1]['can_write'], True)
        self.assertEqual(response_data['data'][role_1]['access_to'], 'something*')

    def test_01_04_get_role_via_api(self):
        # curl -s -D- -X GET 'http://127.0.0.1:5000/api/v1/roles/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/roles/{}?api_key={}'.format(role_1, api_key)
        response = self.app.get(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][role_1]['can_write'], True)
        self.assertEqual(response_data['data'][role_1]['access_to'], 'something*')

    def test_01_05_patch_role_via_api(self):
        # curl -s -D- -X PATCH -d '{"can_write":false}' -H 'Content-type: application/json' 'http://127.0.0.1:5000/api/v1/roles/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/roles/{}?api_key={}'.format(role_1, api_key)
        data = {
            'can_write': True
        }
        response = self.app.patch(url, data = json.dumps(data), content_type = 'application/json')
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][role_1]['can_write'], True)
        self.assertEqual(response_data['data'][role_1]['access_to'], 'something*')

    def test_01_06_get_role_via_api(self):
        # curl -s -D- -X GET 'http://127.0.0.1:5000/api/v1/roles/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/roles/{}?api_key={}'.format(role_1, api_key)
        response = self.app.get(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][role_1]['can_write'], True)
        self.assertEqual(response_data['data'][role_1]['access_to'], 'something*')

    """
    Tests about users
    """

    def test_02_00_get_users_via_api(self):
        # curl -s -D- -X GET 'http://127.0.0.1:5000/api/v1/users?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/users?api_key={}'.format(api_key)
        response = self.app.get(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data']['admin']['email'], 'admin@example.com')
        self.assertEqual(response_data['data']['admin']['labels'], -1)
        self.assertEqual(response_data['data']['admin']['name'], 'Default Administrator')
        self.assertEqual(response_data['data']['admin']['roles'], ['admin'])
        self.assertEqual(response_data['data']['admin']['username'], 'admin')

    def test_02_01_post_user_via_api(self):
        # curl -s -D- -X POST -d '{"username":"test1","password":"test1","labels":100,"email":"user1@example.com","name":"User 1","roles":["admin"]}' -H 'Content-type: application/json' 'http://127.0.0.1:5000/api/v1/users?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/users?api_key={}'.format(api_key)
        data = {
            'email': '{}@example.com'.format(username_1),
            'labels': 100,
            'name': 'User 1',
            'password': password_1,
            'roles': [role_1],
            'username': username_1
        }
        response = self.app.post(url, data = json.dumps(data), content_type = 'application/json')
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][username_1]['email'], '{}@example.com'.format(username_1))
        self.assertEqual(response_data['data'][username_1]['labels'], 100)
        self.assertEqual(response_data['data'][username_1]['name'], 'User 1')
        self.assertEqual(response_data['data'][username_1]['roles'], [role_1])
        self.assertEqual(response_data['data'][username_1]['username'], username_1)

    def test_02_02_get_user_via_api(self):
        # curl -s -D- -X GET 'http://127.0.0.1:5000/api/v1/users/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/users/{}?api_key={}'.format(username_1, api_key)
        response = self.app.get(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][username_1]['email'], '{}@example.com'.format(username_1))
        self.assertEqual(response_data['data'][username_1]['labels'], 100)
        self.assertEqual(response_data['data'][username_1]['name'], 'User 1')
        self.assertEqual(response_data['data'][username_1]['roles'], [role_1])
        self.assertEqual(response_data['data'][username_1]['username'], username_1)

    def test_02_03_auth_via_auth(self):
        # curl -s -D- -u test1:test1 -X GET 'http://127.0.0.1:5000/api/v1/auth'
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(str.encode(username_1) + b':' + str.encode(password_1)).decode('utf-8'),
        }
        url = '/api/v1/auth'
        response = self.app.get(url, headers = headers)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data']['email'], '{}@example.com'.format(username_1))
        self.assertEqual(response_data['data']['labels'], 100)
        self.assertEqual(response_data['data']['name'], 'User 1')
        self.assertEqual(response_data['data']['roles'], [role_1])
        self.assertEqual(response_data['data']['username'], username_1)

    def test_02_04_patch_user_via_api(self):
        # curl -s -D- -X PATCH -d '{"email":"user1@example.org","labels":200,"name":"User A","password":"test2","roles":["admin","test1"]}' -H 'Content-type: application/json' 'http://127.0.0.1:5000/api/v1/users/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/users/{}?api_key={}'.format(username_1, api_key)
        data = {
            'email': '{}@example.org'.format(username_1),
            'labels': 200,
            'name': 'User A',
            'password': password_2,
            'roles': ['admin', role_1],
        }
        response = self.app.patch(url, data = json.dumps(data), content_type = 'application/json')
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][username_1]['email'], '{}@example.org'.format(username_1))
        self.assertEqual(response_data['data'][username_1]['labels'], 200)
        self.assertEqual(response_data['data'][username_1]['name'], 'User A')
        self.assertEqual(response_data['data'][username_1]['roles'], ['admin', role_1])
        self.assertEqual(response_data['data'][username_1]['username'], username_1)

    def test_02_05_auth_via_auth(self):
        # curl -s -D- -u test1:test2 -X GET 'http://127.0.0.1:5000/api/v1/auth'
        headers = {
            'Authorization': 'Basic ' + base64.b64encode(str.encode(username_1) + b':' + str.encode(password_2)).decode('utf-8'),
        }
        url = '/api/v1/auth'
        response = self.app.get(url, headers = headers)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data']['email'], '{}@example.org'.format(username_1))
        self.assertEqual(response_data['data']['labels'], 200)
        self.assertEqual(response_data['data']['name'], 'User A')
        self.assertEqual(response_data['data']['roles'], ['admin', role_1])
        self.assertEqual(response_data['data']['username'], username_1)

    def test_02_06_patch_user_via_api(self):
        # curl -s -D- -X PATCH -d '{"email":"user1@example.net"}' -H 'Content-type: application/json' 'http://127.0.0.1:5000/api/v1/users/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/users/{}?api_key={}'.format(username_1, api_key)
        data = {
            'email': '{}@example.net'.format(username_1),
        }
        response = self.app.patch(url, data = json.dumps(data), content_type = 'application/json')
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][username_1]['email'], '{}@example.net'.format(username_1))
        self.assertEqual(response_data['data'][username_1]['labels'], 200)
        self.assertEqual(response_data['data'][username_1]['name'], 'User A')
        self.assertEqual(response_data['data'][username_1]['roles'], ['admin', role_1])
        self.assertEqual(response_data['data'][username_1]['username'], username_1)

    def test_02_07_get_user_via_api(self):
        # curl -s -D- -X GET 'http://127.0.0.1:5000/api/v1/users/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/users/{}?api_key={}'.format(username_1, api_key)
        response = self.app.get(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')
        self.assertEqual(response_data['data'][username_1]['email'], '{}@example.net'.format(username_1))
        self.assertEqual(response_data['data'][username_1]['labels'], 200)
        self.assertEqual(response_data['data'][username_1]['name'], 'User A')
        self.assertEqual(response_data['data'][username_1]['roles'], ['admin', role_1])
        self.assertEqual(response_data['data'][username_1]['username'], username_1)

    """
    Tests about repositories
    """

    def test_03_00_post_repository_via_api(self):
        # curl -s -D- -X POST -d '{"repository":"test","url":"https://github.com/dainok/rrlabs"}' -H 'Content-type: application/json' http://127.0.0.1:5000/api/v1/repositories?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6
        url = '/api/v1/repositories?api_key={}'.format(api_key)
        data = {
            'repository': 'test',
            'url': 'https://github.com/dainok/rrlabs'
        }
        response = self.app.post(url, data = json.dumps(data), content_type = 'application/json')
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'enqueued')

    def test_03_ff_delete_repository_via_api(self):
        # curl -s -D- -X DELETE http://127.0.0.1:5000/api/v1/repositories/test?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6
        url = 'api/v1/repositories/test{}?api_key={}'.format(api_key)
        response = self.app.delete(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'enqueued')

    """
    Final tests and cleaning
    """

    def test_ff_00_delete_role_via_api(self):
        # curl -s -D- -X DELETE 'http://127.0.0.1:5000/api/v1/roles/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/roles/{}?api_key={}'.format(role_1, api_key)
        response = self.app.delete(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')

    def test_ff_00_delete_user_via_api(self):
        # curl -s -D- -X DELETE 'http://127.0.0.1:5000/api/v1/users/test1?api_key=zqg81ge585t0bt3qe0sjj1idvw7hv7vfgc11dsq6'
        url = '/api/v1/users/{}?api_key={}'.format(username_1, api_key)
        response = self.app.delete(url)
        response_data = json.loads(response.get_data(as_text = True))
        self.assertEqual(response.status_code, 200)
        self.assertEqual(response_data['status'], 'success')

if __name__ == '__main__':
    unittest.main()