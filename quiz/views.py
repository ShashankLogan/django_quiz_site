import random
from django.http import HttpResponse,HttpRequest
from django.contrib.auth.decorators import login_required, permission_required
from django.core.exceptions import PermissionDenied
from django.shortcuts import get_object_or_404, render
from django.utils.decorators import method_decorator
from django.views.generic import DetailView, ListView, TemplateView
from django.views.generic.edit import FormView
from .forms import QuestionForm
from .models import Quiz, Category, Progress, Sitting, Question
from django.shortcuts import render, redirect
from django.contrib.auth import authenticate, login, logout
from django.contrib import messages
from django.template import loader
from django.conf import settings
from importlib import import_module
from django.contrib.auth.models import User

# Quiz.objects.filter(category__category ='A1')
class QuizMarkerMixin(object):
    @method_decorator(login_required)
    @method_decorator(permission_required('quiz.view_sittings'))
    def dispatch(self, *args, **kwargs):
        return super(QuizMarkerMixin, self).dispatch(*args, **kwargs)


class SittingFilterTitleMixin(object):
    def get_queryset(self):
        queryset = super(SittingFilterTitleMixin, self).get_queryset()
        quiz_filter = self.request.GET.get('quiz_filter')
        if quiz_filter:
            queryset = queryset.filter(quiz__title__icontains=quiz_filter)

        return queryset


class QuizListView(ListView):
    model = Quiz
    # @login_required
    def get_queryset(self):
        queryset = super(QuizListView, self).get_queryset()
        return queryset.filter(draft=False)


class QuizDetailView(DetailView):
    model = Quiz
    slug_field = 'url'

    def get(self, request, *args, **kwargs):
        self.object = self.get_object()

        if self.object.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        context = self.get_context_data(object=self.object)
        return self.render_to_response(context)


class CategoriesListView(ListView):
    model = Category

'''
class ViewQuizListByCategory(ListView):
    model = Quiz
    template_name = 'view_quiz_category.html'

    def dispatch(self, request, *args, **kwargs):
        self.category = get_object_or_404(
            Category,
            category=self.kwargs['category_name']
        )

        return super(ViewQuizListByCategory, self).\
            dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(ViewQuizListByCategory, self)\
            .get_context_data(**kwargs)

        context['category'] = self.category
        return context

    def get_queryset(self):
        queryset = super(ViewQuizListByCategory, self).get_queryset()
        return queryset.filter(category=self.category, draft=False)

'''
def ViewQuizListByCategory(request, *args, **kwargs):
    '''
    catego = get_object_or_404(
        Category,
        category=kwargs['category_name']
    )
    '''
    data = Quiz.objects.filter(category__category =kwargs['category_name'])
    if kwargs['category_name'] == "All":
        data = Quiz.objects.all()
    categories = Category.objects.all()
    template = loader.get_template('index.html')
    context = {
        'data': data,
        'categories':categories,
    }
    #return render(request, 'index.html', {})
    return HttpResponse(template.render(context, request))

class QuizUserProgressView(TemplateView):
    template_name = 'progress.html'

    @method_decorator(login_required)
    def dispatch(self, request, *args, **kwargs):
        return super(QuizUserProgressView, self)\
            .dispatch(request, *args, **kwargs)

    def get_context_data(self, **kwargs):
        context = super(QuizUserProgressView, self).get_context_data(**kwargs)
        progress, c = Progress.objects.get_or_create(user=self.request.user)
        context['cat_scores'] = progress.list_all_cat_scores
        context['exams'] = progress.show_exams()
        return context


class QuizMarkingList(QuizMarkerMixin, SittingFilterTitleMixin, ListView):
    model = Sitting

    def get_queryset(self):
        queryset = super(QuizMarkingList, self).get_queryset()\
                                               .filter(complete=True)

        user_filter = self.request.GET.get('user_filter')
        if user_filter:
            queryset = queryset.filter(user__username__icontains=user_filter)

        return queryset

    class Meta:
        pass


class QuizMarkingDetail(QuizMarkerMixin, DetailView):
    model = Sitting

    def post(self, request, *args, **kwargs):
        sitting = self.get_object()

        q_to_toggle = request.POST.get('qid', None)
        if q_to_toggle:
            q = Question.objects.get_subclass(id=int(q_to_toggle))
            if int(q_to_toggle) in sitting.get_incorrect_questions:
                sitting.remove_incorrect_question(q)
            else:
                sitting.add_incorrect_question(q)

        return self.get(request)

    def get_context_data(self, **kwargs):
        context = super(QuizMarkingDetail, self).get_context_data(**kwargs)
        context['questions'] =\
            context['sitting'].get_questions(with_answers=True)
        return context


class QuizTake(FormView):
    form_class = QuestionForm
    template_name = 'question.html'
    def dispatch(self, request, *args, **kwargs):
        '''
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.request.META['useranme'] = 'Shashank'
        self.request.META['password'] = 'shashank'
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        self.request.session = engine.SessionStore(session_key)
        #user = User.objects.get(username='Shashank')
        self.request.user = authenticate(username='Shashank', password='shashank')
        login(self.request,self.request.user)
        '''

        self.quiz = get_object_or_404(Quiz, url=self.kwargs['quiz_name'])

        if self.quiz.draft and not request.user.has_perm('quiz.change_quiz'):
            raise PermissionDenied

        self.logged_in_user = self.request.user.is_authenticated

        if self.logged_in_user:
            self.sitting = Sitting.objects.user_sitting(self.request.user, self.quiz)




        if self.sitting is False:
            return render(request, 'single_complete.html')

        return super(QuizTake, self).dispatch(request, *args, **kwargs)

    def get_form(self, form_class=QuestionForm):
        '''
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.request.META['useranme'] = 'Shashank'
        self.request.META['password'] = 'shashank'
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        self.request.session = engine.SessionStore(session_key)
        #user = User.objects.get(username='Shashank')
        self.request.user = authenticate(username='Shashank', password='shashank')
        login(self.request,self.request.user)
        '''
        #if self.logged_in_user:
        if True:
            print(self)
            self.question = self.sitting.get_first_question()
            print("1!!!!!question")
            print(self.question)
            self.progress = self.sitting.progress()
            print("1!!!!!progress")
            print(self.progress)
        return form_class(**self.get_form_kwargs())

    def get_form_kwargs(self):
        kwargs = super(QuizTake, self).get_form_kwargs()

        return dict(kwargs, question=self.question)

    def form_valid(self, form):
        #if self.logged_in_user:
        if True:
            self.form_valid_user(form)
            if self.sitting.get_first_question() is False:
                return self.final_result_user()
            self.request.POST = {}

        return super(QuizTake, self).get(self, self.request)

    def get_context_data(self, **kwargs):
        context = super(QuizTake, self).get_context_data(**kwargs)
        context['question'] = self.question
        context['quiz'] = self.quiz
        if hasattr(self, 'previous'):
            context['previous'] = self.previous
        if hasattr(self, 'progress'):
            context['progress'] = self.progress
        return context

    def form_valid_user(self, form):
        '''
        self.request = HttpRequest()
        self.request.method = 'POST'
        self.request.META['useranme'] = 'Shashank'
        self.request.META['password'] = 'shashank'
        engine = import_module(settings.SESSION_ENGINE)
        session_key = None
        self.request.session = engine.SessionStore(session_key)
        #user = User.objects.get(username='Shashank')
        self.request.user = authenticate(username='Shashank', password='shashank')
        login(self.request,self.request.user)
        '''
        #progress, c = Progress.objects.get_or_create(user=self.request.user)
        progress, c = Progress.objects.get_or_create(user=authenticate(username='Shashank', password='shashank'))
        guess = form.cleaned_data['answers']
        is_correct = self.question.check_if_correct(guess)

        if is_correct is True:
            self.sitting.add_to_score(1)
            progress.update_score(self.question, 1, 1)
        else:
            self.sitting.add_incorrect_question(self.question)
            progress.update_score(self.question, 0, 1)

        if self.quiz.answers_at_end is not True:
            self.previous = {'previous_answer': guess,
                             'previous_outcome': is_correct,
                             'previous_question': self.question,
                             'answers': self.question.get_answers(),
                             'question_type': {self.question
                                               .__class__.__name__: True}}
        else:
            self.previous = {}

        self.sitting.add_user_answer(self.question, guess)
        self.sitting.remove_first_question()

    def final_result_user(self):
        results = {
            'quiz': self.quiz,
            'score': self.sitting.get_current_score,
            'max_score': self.sitting.get_max_score,
            'percent': self.sitting.get_percent_correct,
            'sitting': self.sitting,
            'previous': self.previous,
        }

        self.sitting.mark_quiz_complete()

        if self.quiz.answers_at_end:
            results['questions'] =\
                self.sitting.get_questions(with_answers=True)
            results['incorrect_questions'] =\
                self.sitting.get_incorrect_questions

        if self.quiz.exam_paper is False:
            self.sitting.delete()

        return render(self.request, 'result.html', results)




def index(request):
    login_user(request)
    data = Quiz.objects.all()
    categories = Category.objects.all()
    template = loader.get_template('index.html')
    context = {
        'data': data,
        'categories':categories,
    }
    #return render(request, 'index.html', {})
    return HttpResponse(template.render(context, request))


def login_user(request):
    #request = HttpRequest()
    request.method = 'POST'
    request.META['username'] = 'user'
    request.META['password'] = 'user1234'
    engine = import_module(settings.SESSION_ENGINE)
    session_key = None
    request.session = engine.SessionStore(session_key)
    # user = User.objects.get(username='Shashank')
    request.user = authenticate(username='user', password='user1234')
    #login(self.request, self.request.user)

    if request.method == 'POST':
        #username = request.POST['username']
        #password = request.POST['password']
        user = authenticate(username='user', password='user1234') #authenticate(request, username=username, password=password)
        if user is not None:
            login(request, user)
            #messages.success(request, 'You have successfully logged in')
            return redirect("index")
        else:
            messages.success(request, 'Error logging in')
            return redirect('login')
    else:
        return render(request, 'login.html', {})


def logout_user(request):
    logout(request)
    messages.success(request, 'You have been logged out!')
    print('logout function working')
    return redirect('login')

