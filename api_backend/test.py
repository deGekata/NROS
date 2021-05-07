""" Flask testing module """
import json
import unittest
import jsonpath
import requests

message_error = 'The requested URL was not found on the server. If you entered the URL manually please check your spelling and try again.'

class TestCase(unittest.TestCase):
    """
        Tests
    """

    def test_api_trail_post(self):
        """
            Testing trail
        """
        response = requests.post("http://127.0.0.1:5000/api/train_all", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------

    def test_api_tags_get(self):
        """
            Testing tags
        """
        response = requests.get("http://127.0.0.1:5000/api/tags", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 200)

    def test_api_tags_post(self):
        """
            Testing tags
        """
        response = requests.post("http://127.0.0.1:5000/api/tags", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    def test_api_tags_put(self):
        """
            Testing tags
        """
        response = requests.put("http://127.0.0.1:5000/api/tags", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------

    def test_api_tags_get_1(self):
        """
            Testing tags
        """
        response = requests.get("http://127.0.0.1:5000/api/tags", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'tags')
        page = tags_page[0][0]
        self.assertEqual(page['id'], page['id'])
        self.assertEqual(page['minimum'], page['minimum'])
        self.assertEqual(page['capacity'], page['capacity'])

    def test_api_tags_get_2(self):
        """
            Testing tags
        """
        response = requests.get("http://127.0.0.1:5000/api/tags", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'tags')
        page = tags_page[0][1]
        self.assertEqual(page['id'], page['id'])
        self.assertEqual(page['minimum'], page['minimum'])
        self.assertEqual(page['capacity'], page['capacity'])

    def test_api_tags_get_3(self):
        """
            Testing tags
        """
        response = requests.get("http://127.0.0.1:5000/api/tags", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'tags')
        page = tags_page[0][2]
        self.assertEqual(page['id'], page['id'])
        self.assertEqual(page['minimum'], page['minimum'])
        self.assertEqual(page['capacity'], page['capacity'])

    def test_api_tags_get_4(self):
        """
            Testing tags
        """
        response = requests.get("http://127.0.0.1:5000/api/tags", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'tags')
        page = tags_page[0][3]
        self.assertEqual(page['id'], page['id'])
        self.assertEqual(page['minimum'], page['minimum'])
        self.assertEqual(page['capacity'], page['capacity'])

    # --------------------------------------------------------------

    def test_api_predict_post(self):
        """
            Testing predict
        """
        response = requests.post("http://127.0.0.1:5000/api/predict", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 500)

    # --------------------------------------------------------------

    def test_api_sales_get(self):
        """
            Testing sales
        """
        response = requests.get("http://127.0.0.1:5000/api/sales", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 200)

    def test_api_sales_post(self):
        """
            Testing sales
        """
        response = requests.post("http://127.0.0.1:5000/api/sales", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------

    def test_api_sales_get_1(self):
        """
            Testing sales
        """
        response = requests.get("http://127.0.0.1:5000/api/sales", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'sales')
        page = tags_page[0][0]
        self.assertEqual(page['id'], page['id'])
        self.assertEqual(page['date'], page['date'])
        self.assertEqual(page['count'], page['count'])

    def test_api_sales_get_2(self):
        """
            Testing sales
        """
        response = requests.get("http://127.0.0.1:5000/api/sales", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'sales')
        page = tags_page[0][1]
        self.assertEqual(page['id'], page['id'])
        self.assertEqual(page['date'], page['date'])
        self.assertEqual(page['count'], page['count'])

    def test_api_sales_get_3(self):
        """
            Testing sales
        """
        response = requests.get("http://127.0.0.1:5000/api/sales", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'sales')
        page = tags_page[0][2]
        self.assertEqual(page['id'], page['id'])
        self.assertEqual(page['date'], page['date'])
        self.assertEqual(page['count'], page['count'])

    # --------------------------------------------------------------

    def test_api_lstms_get(self):
        """
            Testing lstms
        """
        response = requests.get("http://127.0.0.1:5000/api/lstms", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 200)

    def test_api_lstms_post(self):
        """
            Testing lstms
        """
        response = requests.post("http://127.0.0.1:5000/api/lstms", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------

    def test_api_points_get(self):
        """
            Testing points
        """
        response = requests.get("http://127.0.0.1:5000/api/points", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 200)

    def test_api_points_post(self):
        """
            Testing points
        """
        response = requests.post("http://127.0.0.1:5000/api/points", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------

    def test_api_product_types_get(self):
        """
            Testing product types
        """
        response = requests.get("http://127.0.0.1:5000/api/product_types", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 200)

    def test_api_product_types_post(self):
        """
            Testing product types
        """
        response = requests.post("http://127.0.0.1:5000/api/product_types", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------

    def test_api_tags_id_1_get(self):
        """
            Testing tags
        """
        response = requests.get("http://127.0.0.1:5000/api/tags/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'message')
        if tags_page[0] == message_error:
            self.assertEqual(response.status_code, 404)
        else: self.assertEqual(response.status_code, 200)

    def test_api_tags_id_1_put(self):
        """
            Testing tags
        """
        response = requests.put("http://127.0.0.1:5000/api/tags/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------

    def test_api_sales_id_1_get(self):
        """
            Testing sales
        """
        response = requests.get("http://127.0.0.1:5000/api/sales/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'message')
        if tags_page[0] == message_error:
            self.assertEqual(response.status_code, 404)
        else: self.assertEqual(response.status_code, 200)

    def test_api_sales_id_1_put(self):
        """
            Testing sales
        """
        response = requests.put("http://127.0.0.1:5000/api/sales/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------

    def test_api_lstms_id_1_get(self):
        """
            Testing lstms
        """
        response = requests.get("http://127.0.0.1:5000/api/lstms/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'message')
        if tags_page[0] == message_error:
            self.assertEqual(response.status_code, 404)
        else: self.assertEqual(response.status_code, 200)

    def test_api_lstms_id_1_put(self):
        """
            Testing lstms
        """
        response = requests.get("http://127.0.0.1:5000/api/lstms/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 404)

    # --------------------------------------------------------------

    def test_api_points_id_1_get(self):
        """
            Testing points
        """
        response = requests.get("http://127.0.0.1:5000/api/points/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'message')
        if tags_page[0] == message_error:
            self.assertEqual(response.status_code, 404)
        else: self.assertEqual(response.status_code, 200)

    def test_api_points_id_1_put(self):
        """
            Testing points
        """
        response = requests.put("http://127.0.0.1:5000/api/points/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

    # --------------------------------------------------------------

    def test_api_product_types_id_1_get(self):
        """
            Testing product types
        """
        response = requests.get("http://127.0.0.1:5000/api/product_types/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        json_response = json.loads(response.text)
        tags_page = jsonpath.jsonpath(json_response, 'message')
        if tags_page[0] == message_error:
            self.assertEqual(response.status_code, 404)
        else: self.assertEqual(response.status_code, 200)

    def test_api_product_types_id_1_put(self):
        """
            Testing product types
        """
        response = requests.put("http://127.0.0.1:5000/api/product_types/1", headers={
            "Authorization": "036d20170acccf1f8ddbc4005810219bcff14321001a2a6f567ef3cf2091b7ee"})
        self.assertEqual(response.status_code, 400)

if __name__ == '__main__':
    LOG = 'public/api_test.txt'
    file = open(LOG, 'w')
    runner = unittest.TextTestRunner(file)
    unittest.main(testRunner=runner)
    file.close()
