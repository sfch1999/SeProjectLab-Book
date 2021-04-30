import django
from django.http import HttpResponse
from rest_framework import viewsets
import requests

from Books.models import Book


class BookAPI(viewsets.ViewSet):
    def handle_request(self, request):
        try:
            req = request.data['request']
        except KeyError:
            return HttpResponse('Required fields are empty!!!', status=406)
        user = self.get_user_role(request.data)
        if user == 'Token not valid':
            return HttpResponse('Token not valid', status=409)

        if req == 'Read':
            try:
                search_by = 'tit'
                to_search = request.data['title']
            except KeyError:
                try:
                    search_by = 'cat'
                    to_search = request.data['category']
                except KeyError:
                    return HttpResponse('Required fields are empty!!!', status=406)
            if search_by == 'tit':
                try:
                    book = Book.objects.get(title=to_search)
                except:
                    return HttpResponse('Title not valid', status=409)
                if not book:
                    return HttpResponse('Title not valid', status=409)
                return HttpResponse(
                    'Title: ' + book.title + '\nAuthors: ' + book.authors + '\nCategory: ' + book.category,
                    status=200)
            elif search_by == 'cat':
                try:
                    books = Book.objects.filter(category=to_search)
                except:
                    return HttpResponse('Category not valid', status=409)
                if not books:
                    return HttpResponse('Category not valid', status=409)
                str_to_return = ''
                for book in books:
                    str_to_return += '[' + 'Title: ' + book.title + '\nAuthors: ' + book.authors + '\nCategory: ' + book.category + ']\n'
                return HttpResponse(str_to_return, status=200)

        if req == 'Create':
            if not user:
                return HttpResponse('Unauthorized', status=401)
            try:
                title = request.data['title']
                authors = request.data['authors']
                category = request.data['category']
            except KeyError:
                return HttpResponse('Required fields are empty!!!', status=406)
            book = Book()
            book.title, book.authors, book.category = title, authors, category
            try:
                book.save()
            except django.db.utils.IntegrityError:
                return HttpResponse('Conflict', status=409)
            return HttpResponse('The book created', status=200)

        if req == 'Delete':
            if not user:
                return HttpResponse('Unauthorized', status=401)
            try:
                title = request.data['title']
            except KeyError:
                return HttpResponse('Required fields are empty!!!', status=406)
            try:
                book = Book.objects.get(title=title)
            except:
                return HttpResponse('Title not valid', status=409)
            if not book:
                return HttpResponse('Title not valid', status=409)
            book.delete()
            return HttpResponse(
                'Book deleted!',
                status=200)
        if req == 'Update':
            if not user:
                return HttpResponse('Unauthorized', status=401)
            try:
                title = request.data['title']
                try:
                    book = Book.objects.get(title=title)
                except:
                    return HttpResponse('Title not valid', status=409)
            except KeyError:
                return HttpResponse('Required fields are empty!!!', status=406)
            try:
                new_title = request.data['new_title']
                book.title = new_title
            except KeyError:
                pass
            try:
                new_authors = request.data['new_authors']
                book.authors = new_authors
            except KeyError:
                pass
            try:
                new_cat = request.data['new_category']
                book.category = new_cat
            except KeyError:
                pass
            try:
                book.save()
            except django.db.utils.IntegrityError:
                return HttpResponse('Conflict', status=409)
            return HttpResponse('The book updated', status=200)

    @staticmethod
    def get_user_role(data):
        url = 'http://127.0.0.1:8000/api/token'
        response = requests.post(url, data=data, timeout=0.500)
        if response.status_code / 100 == 4:
            return 'Token not valid'
        else:
            return response.text
