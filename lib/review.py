# lib/models/review.py

from lib import CONN, CURSOR
from lib.models.employee import Employee

class Review:
    all = {}

    def __init__(self, year, summary, employee):
        self.id = None
        self.year = year
        self.summary = summary
        self.employee = employee

    def __repr__(self):
        return f"<Review id={self.id} year={self.year} summary={self.summary} employee_id={self.employee.id}>"

    @classmethod
    def create_table(cls):
        CURSOR.execute("""
            CREATE TABLE IF NOT EXISTS reviews (
                id INTEGER PRIMARY KEY,
                year INTEGER NOT NULL,
                summary TEXT NOT NULL,
                employee_id INTEGER NOT NULL,
                FOREIGN KEY (employee_id) REFERENCES employees (id)
            )
        """)
        CONN.commit()

    @classmethod
    def drop_table(cls):
        CURSOR.execute("DROP TABLE IF EXISTS reviews")
        CONN.commit()

    def save(self):
        if self.id is None:
            CURSOR.execute("""
                INSERT INTO reviews (year, summary, employee_id) VALUES (?, ?, ?)
            """, (self.year, self.summary, self.employee.id))
            self.id = CURSOR.lastrowid
            self.__class__.all[self.id] = self
        else:
            CURSOR.execute("""
                UPDATE reviews SET year=?, summary=?, employee_id=? WHERE id=?
            """, (self.year, self.summary, self.employee.id, self.id))
        CONN.commit()

    @classmethod
    def create(cls, year, summary, employee_id):
        employee = Employee.find_by_id(employee_id)
        if employee is None:
            raise ValueError("Employee not found")
        review = cls(year, summary, employee)
        review.save()
        return review

    @classmethod
    def instance_from_db(cls, row):
        if row[0] in cls.all:
            return cls.all[row[0]]
        employee = Employee.find_by_id(row[3])
        review = cls(row[1], row[2], employee)
        review.id = row[0]
        cls.all[row[0]] = review
        return review

    @classmethod
    def find_by_id(cls, review_id):
        CURSOR.execute("SELECT * FROM reviews WHERE id=?", (review_id,))
        row = CURSOR.fetchone()
        if row is None:
            return None
        return cls.instance_from_db(row)

    def update(self):
        self.save()

    def delete(self):
        CURSOR.execute("DELETE FROM reviews WHERE id=?", (self.id,))
        del self.__class__.all[self.id]
        self.id = None
        CONN.commit()

    @classmethod
    def get_all(cls):
        CURSOR.execute("SELECT * FROM reviews")
        rows = CURSOR.fetchall()
        return [cls.instance_from_db(row) for row in rows]

    @property
    def year(self):
        return self._year

    @year.setter
    def year(self, value):
        if not isinstance(value, int) or value < 2000:
            raise ValueError("Year must be an integer greater than or equal to 2000")
        self._year = value

    @property
    def summary(self):
        return self._summary

    @summary.setter
    def summary(self, value):
        if not isinstance(value, str) or len(value) == 0:
            raise ValueError("Summary must be a non-empty string")
        self._summary = value

    @property
    def employee(self):
        return self._employee

    @employee.setter
    def employee(self, value):
        if not isinstance(value, Employee):
            raise ValueError("Employee must be an instance of Employee class")
        self._employee = value
