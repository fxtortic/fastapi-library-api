from locust import HttpUser, task, between


class LibraryUser(HttpUser):
    wait_time = between(1, 3)
    host = "http://api:8000"

    def on_start(self):
        """Register and login to get token"""
        import random
        self.username = f"user_{random.randint(1, 1_000_000)}"
        self.client.post("/auth/register", json={
            "username": self.username,
            "password": "testpass123",
        })
        resp = self.client.post("/auth/login", json={
            "username": self.username,
            "password": "testpass123",
        })
        token = resp.json()["access_token"]
        self.headers = {"Authorization": f"Bearer {token}"}

        # create some books
        for i in range(3):
            self.client.post("/books/", json={
                "title": f"Book {i}",
                "author": "Author",
                "description": "Description",
                "status": "available",
                "year": 2020 + i,
            }, headers=self.headers)

    @task
    def get_books(self):
        self.client.get("/books/", headers=self.headers)