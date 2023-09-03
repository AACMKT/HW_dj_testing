import pytest
from rest_framework.test import APIClient
from model_bakery import baker
from students.models import Course, Student


@pytest.fixture
def api_client():
    return APIClient()


@pytest.fixture
def students_factory():
    def factory(*args, **kwargs):
        return baker.make(Student, *args, **kwargs)

    return factory


@pytest.fixture
def courses_factory():
    def factory(*args, **kwargs):
        return baker.make(Course, *args, **kwargs)

    return factory


@pytest.mark.django_db
def test_get_course(api_client, courses_factory):
    # Arrange
    course = courses_factory(_quantity=1, id=1)
    # Act
    response = api_client.get('/api/v1/courses/1/')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data['name'] == course[0].name
    assert data['id'] == course[0].pk


@pytest.mark.django_db
def test_list_courses(api_client, courses_factory):
    # Arrange
    courses = courses_factory(_quantity=10)
    db = Course.objects.all()
    # Act
    response = api_client.get('/api/v1/courses/')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert len(data) == len(db)
    for i, v in enumerate(courses):
        assert data[i]['name'] == v.name
        assert data[i]['id'] == v.pk


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, courses_factory):
    # Arrange
    courses = courses_factory(_quantity=10)
    _id = courses[0].pk
    # Act
    response = api_client.get(f'/api/v1/courses/?id={_id}')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['id'] == _id


@pytest.mark.django_db
def test_filter_courses_by_id(api_client, courses_factory):
    # Arrange
    courses = courses_factory(_quantity=10)
    _name = courses[0].name
    # Act
    response = api_client.get(f'/api/v1/courses/?name={_name}')
    data = response.json()

    # Assert
    assert response.status_code == 200
    assert data[0]['name'] == _name


@pytest.mark.django_db
def test_create_course(api_client):
    count = Course.objects.count()
    response = api_client.post('/api/v1/courses/', data={'name': 'test_name'})
    data = response.json()

    assert response.status_code == 201
    assert data['name'] == 'test_name'
    assert Course.objects.count() == count + 1


@pytest.mark.django_db
def test_change_course(api_client, courses_factory):

    courses = courses_factory(_quantity=10)
    _id = courses[0].pk

    response = api_client.patch(f'/api/v1/courses/{_id}/', data={'name': 'test_name_new'})
    data = response.json()

    assert response.status_code == 200
    assert data['id'] == _id
    assert data['name'] == 'test_name_new'


@pytest.mark.django_db
def test_check_students_number(api_client, settings, students_factory, courses_factory):
    students = baker.prepare(Student, _quantity=20)
    courses = courses_factory(_quantity=1, students=students)
    _id = courses[0].pk
    response = api_client.get(f'/api/v1/courses/{_id}/')
    data = response.json()

    assert response.status_code == 200
    assert data['id'] == _id
    assert settings.MAX_STUDENTS_PER_COURSE == len(data['students'])
    settings.MAX_STUDENTS_PER_COURSE += 1
    assert settings.MAX_STUDENTS_PER_COURSE != len(data['students'])
