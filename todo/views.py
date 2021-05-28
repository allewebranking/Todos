from django.shortcuts import render, redirect, get_object_or_404
from django.contrib.auth.forms import UserCreationForm, AuthenticationForm
from django.contrib.auth.models import User
from django.db import IntegrityError
from django.contrib.auth import login, logout, authenticate
from .forms import TodoForm
from .models import todo
from django.utils import timezone
from django.contrib.auth.decorators import login_required
# Create your views here.
def home(request):

    return render(request, 'todo/home.html')

def signupuser(request):
    if request.method =='GET':
        return render(request,'todo/signupuser.html',{'form':UserCreationForm()})
    else:
        #create new user
        if request.POST['password1'] ==request.POST['password2']:
            try:
                user = User.objects.create_user(request.POST['username'],password=request.POST['password1'])
                user.save()
                login(request, user)
                return redirect('currentTodos')
            except IntegrityError:
                return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':"Username già preso, prova a sceglierne un altro"})


        else:
            #le password non coincidono
            print("le password non coincidono")
            return render(request,'todo/signupuser.html',{'form':UserCreationForm(),'error':"le password non coincidono"})

@login_required
def currentTodos(request):
        todos = todo.objects.filter(user=request.user, date_completed__isnull=True)
        return render(request,'todo/currentTodos.html',{'todos':todos})

@login_required
def completed(request):
        todos = todo.objects.filter(user=request.user, date_completed__isnull=False).order_by('-date_completed')
        return render(request,'todo/completed.html',{'todos':todos})

def loginuser(request):

    if request.method =='GET':
        return render(request,'todo/loginuser.html',{'form':AuthenticationForm()})
    else:
        user = authenticate(request,username=request.POST['username'],password=request.POST['password'])
        if user is None:
            return  render(request,'todo/loginuser.html',{'form':AuthenticationForm(),'error':"L'username o la password non sono corretti"})
        else:
            login(request, user)
            return redirect('currentTodos')

@login_required
def logoutuser(request):
    if request.method == 'POST':
        logout(request)
        return redirect('home')

@login_required
def createTodo(request):
        if request.method =='GET':
            return render(request,'todo/createTodo.html',{'form':TodoForm()})
        else:
            try:
                form = TodoForm(request.POST)
                newTodo = form.save(commit=False)
                newTodo.user = request.user
                newTodo.save()
                return redirect('currentTodos')
            except ValueError:
                    return render(request,'todo/createTodo.html',{'form':TodoForm(),'error':'errore sui dati inseriti, riprova'})

@login_required
def viewtodos(request, todo_pk):
        Todo = get_object_or_404(todo, pk=todo_pk, user=request.user)
        if request.method =='GET':
            form = TodoForm(instance=Todo)
            return render(request,'todo/viewtodos.html',{'todo':Todo,'form':form})
        else:
            try:
                form = TodoForm(request.POST,instance=Todo)
                form.save()
                return redirect('currentTodos')
            except ValueError:
                return render(request,'todo/viewtodos.html',{'todo':Todo,'form':form,'error':'sono stati passati dei dati errati'})

@login_required
def completetodos(request, todo_pk):
    Todo = get_object_or_404(todo, pk=todo_pk, user=request.user)
    if request.method =='POST':
        Todo.date_completed = timezone.now()
        Todo.save()
        return redirect('currentTodos')

@login_required
def delete(request, todo_pk):
    Todo = get_object_or_404(todo, pk=todo_pk, user=request.user)
    if request.method =='POST':
        Todo.date_completed = timezone.now()
        Todo.delete()
        return redirect('currentTodos')
    else:
        pass
