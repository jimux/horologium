from django.contrib.auth.models import User
from rest_framework import status
from rest_framework.test import APITestCase
import time

PASSWORD = 'password'

users = ['admin', 'user1']
who_access = {
    "users": {
        'create_new': ['admin', 'user1'],
        'delete': ['admin']
    },
    "groups": {},
    "timers": {},
    "durations": {},
    "countdowns": {},
    "notes": {}
}

class ClockTestCase(APITestCase):
    def post(self, path, obj, expected_status=status.HTTP_201_CREATED):
        response = self.client.post('/api/v1/' + path, obj, format='json')
        self.assertEqual(response.status_code, expected_status, msg=response)
        return response.data

    # Why is 200 the default return code for put and patch?
    def put(self, path, obj, expected_status=status.HTTP_200_OK):
        response = self.client.put('/api/v1/' + path, obj, format='json')
        self.assertEqual(response.status_code, expected_status, msg=response)
        return response.data

    def patch(self, path, obj, expected_status=status.HTTP_200_OK):
        response = self.client.patch('/api/v1/' + path, obj, format='json')
        self.assertEqual(response.status_code, expected_status, msg=response)
        return response.data

    def get(self, path, expected_status=status.HTTP_200_OK):
        response = self.client.get('/api/v1/' + path, format='json')
        self.assertEqual(response.status_code, expected_status, msg=response)
        return response.data

    def delete(self, path, expected_status=status.HTTP_204_NO_CONTENT):
        response = self.client.delete('/api/v1/' + path, format='json')
        self.assertEqual(response.status_code, expected_status, msg=response)
        return response.data

    def options(self, path, expected_status):
        response = self.client.options('/api/v1/' + path, format='json')
        self.assertEqual(response.status_code, expected_status, msg=response)
        return response.data

    def create_user(self, username):
        email = username + "@local.local"
        user = {'email': email, 'username': username, 'password': PASSWORD}
        return self.post('signup/', user, status.HTTP_201_CREATED)['id']

    def login(self, username):
        self.assertTrue(self.client.login(username=username, password=PASSWORD))

    def logout(self):
        self.client.logout()

    def setUp(self):
        self.superuser = User.objects.create_superuser('admin', 'local@local.local', PASSWORD)
        users.append('admin')

        self.user1_id = self.create_user('user1')
        self.user2_id = self.create_user('user2')

    def test_noaccess(self):
        """No one is logged in. Nothing should be accessible."""

        endpoint = "signup"
        self.get(endpoint + "/", status.HTTP_405_METHOD_NOT_ALLOWED)
        self.put(endpoint + "/", {}, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.patch(endpoint + "/", {}, status.HTTP_405_METHOD_NOT_ALLOWED)
        self.delete(endpoint + "/", status.HTTP_405_METHOD_NOT_ALLOWED)
        self.options(endpoint + "/", status.HTTP_200_OK)

        endpoints = ['users', 'timers', 'durations', 'countdowns', 'notes']
        for endpoint in endpoints:
            self.get(endpoint + "/", status.HTTP_403_FORBIDDEN)
            self.post(endpoint + "/", {}, status.HTTP_403_FORBIDDEN)
            self.put(endpoint + "/", {}, status.HTTP_403_FORBIDDEN)
            self.patch(endpoint + "/", {}, status.HTTP_403_FORBIDDEN)
            self.delete(endpoint + "/", status.HTTP_403_FORBIDDEN)
            self.options(endpoint + "/", status.HTTP_403_FORBIDDEN)

    def test_start_stop_mark(self):
        """
        A user can start, mark, and stop a timer, as well as get total time. User 2 can't interact with User 1's timer.
        """
        self.login('user1')
        timer = self.post('timers/', {'durations': [], 'countdowns': []}, status.HTTP_201_CREATED)
        self.assertEqual(len(timer['durations']), 0)
        self.put('timers/%s/start/' % timer['id'], {})
        timer = self.get('timers/%s/' % timer['id'])
        self.assertEqual(len(timer['durations']), 1)

        time.sleep(1)

        self.put('timers/%s/mark/' % timer['id'], {})
        timer = self.get('timers/%s/' % timer['id'])

        self.assertEqual(len(timer['durations']), 2)
        self.assertGreaterEqual(timer['elapsed'], 1)
        self.assertLess(timer['elapsed'], 2)

        time.sleep(1)

        self.put('timers/%s/stop/' % timer['id'], {})
        # Should have elapsed at least two seconds. If longer than three, this test has issues...
        timer = self.get('timers/%s/' % timer['id'])

        data = self.get('timers/%s/durations' % timer['id'])
        self.assertEqual(len(data), 2)

        self.assertGreaterEqual(timer['elapsed'], 2)
        self.assertLess(timer['elapsed'], 3)
        self.logout()

        self.login('user2')
        self.put('timers/%s/start/' % timer['id'], {}, status.HTTP_404_NOT_FOUND)
        self.put('timers/%s/mark/' % timer['id'], {}, status.HTTP_404_NOT_FOUND)
        self.put('timers/%s/stop/' % timer['id'], {}, status.HTTP_404_NOT_FOUND)
        self.logout()

    def test_can_or_cant_access_basic(self):
        """
        User 1 can create and modify their stuff. User 2 can't modify User 1's stuff.
        """
        self.login('user1')
        timer = self.post('timers/', {'durations': [], 'countdowns': []}, status.HTTP_201_CREATED)
        timer2 = self.post('timers/', {'durations': [], 'countdowns': []}, status.HTTP_201_CREATED)
        duration = self.post('durations/', {'timer': timer['id']}, status.HTTP_201_CREATED)
        countdown = self.post('countdowns/', {'timer': timer['id'], 'count': 60}, status.HTTP_201_CREATED)
        note = self.post('notes/', {'note': 'blah'}, status.HTTP_201_CREATED)
        self.logout()

        # User 2 can't touch these.
        self.login('user2')
        self.delete('timers/%s/' % timer['id'], status.HTTP_404_NOT_FOUND)
        self.put('timers/%s/' % timer['id'], {}, status.HTTP_404_NOT_FOUND)
        self.patch('timers/%s/' % timer['id'], {}, status.HTTP_404_NOT_FOUND)
        # Setting a different user as owner won't work. Defaults to current user.
        user2_timer = self.post('timers/', {'durations': [], 'countdowns': [], 'owner': self.user1_id}, status.HTTP_201_CREATED)
        self.assertEqual(user2_timer['owner'], self.user2_id)

        self.delete('durations/%s/' % duration['id'], status.HTTP_404_NOT_FOUND)
        self.put('durations/%s/' % duration['id'], {}, status.HTTP_404_NOT_FOUND)
        self.patch('durations/%s/' % duration['id'], {}, status.HTTP_404_NOT_FOUND)
        # Can't set to someone else's timer.
        self.post('durations/', {'timer': timer['id']}, status.HTTP_400_BAD_REQUEST)

        self.delete('countdowns/%s/' % countdown['id'], status.HTTP_404_NOT_FOUND)
        self.put('countdowns/%s/' % countdown['id'], {}, status.HTTP_404_NOT_FOUND)
        self.patch('countdowns/%s/' % countdown['id'], {}, status.HTTP_404_NOT_FOUND)
        # Can't set to someone else's timer.
        self.post('countdowns/', {'timer': timer['id']}, status.HTTP_400_BAD_REQUEST)

        self.delete('notes/%s/' % note['id'], status.HTTP_404_NOT_FOUND)
        self.put('notes/%s/' % note['id'], {}, status.HTTP_404_NOT_FOUND)
        self.patch('notes/%s/' % note['id'], {}, status.HTTP_404_NOT_FOUND)
        # Setting a different user as writer won't work. Defaults to current user.
        user2_note = self.post('notes/', {'note': 'blah', 'writer': self.user1_id}, status.HTTP_201_CREATED)
        self.assertEqual(user2_note['writer'], self.user2_id)
        self.logout()

        # User 1 can.
        self.login('user1')

        self.put('durations/%s/' % duration['id'], {'timer': timer['id']})
        self.patch('durations/%s/' % duration['id'], {'timer': timer2['id']})
        self.assertEqual(self.get('durations/%s/' % duration['id'])['timer'], timer2['id'])
        self.delete('durations/%s/' % duration['id'])

        self.put('countdowns/%s/' % countdown['id'], {'timer': timer['id'], 'count': 60})
        self.patch('countdowns/%s/' % countdown['id'], {'timer': timer2['id']})
        self.assertEqual(self.get('countdowns/%s/' % countdown['id'])['timer'], timer2['id'])
        self.delete('countdowns/%s/' % countdown['id'])

        self.put('timers/%s/' % timer['id'], {'durations': [], 'countdowns': []})
        self.patch('timers/%s/' % timer['id'], {'name': 'testname'})
        self.assertEqual(self.get('timers/%s/' % timer['id'])['name'], 'testname')
        self.delete('timers/%s/' % timer['id'])
        self.logout()
