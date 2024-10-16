from django.shortcuts import render, redirect, get_object_or_404
from django.http import HttpResponseRedirect
from .models import Task
from .forms import TaskForm
from django.contrib.auth.decorators import login_required
from django.urls import reverse


# Create your views here.
@login_required
def dashboard(request, task_id=None):
    # Get active and completed tasks for the user
    active_tasks = Task.objects.filter(user=request.user, status__in=[0, 1])  # 0: Not Started, 1: In Progress
    completed_tasks = Task.objects.filter(user=request.user, status=2)  # 2: Completed

    # Handle task creation or editing
    if task_id:
        task = get_object_or_404(Task, id=task_id, user=request.user)  # For editing
    else:
        task = None  # For creating a new task

    if request.method == 'POST':
        if task_id:
            task = get_object_or_404(Task, id=task_id, user=request.user)
            form = TaskForm(request.POST, instance=task)
        else:
            form = TaskForm(request.POST)
        
        if form.is_valid():
            task = form.save(commit=False)
            task.user = request.user
            task.save()
            return redirect('dashboard')
    else:
        form = TaskForm(instance=task) if task_id else TaskForm()
            
    # Handle search query
    query = request.GET.get('q', '').strip()
    if query:
        search_results = Task.objects.filter(user=request.user, title__icontains=query)
        if not search_results.exists():  # This checks if no tasks match the search
            search_results = []  # This will return an empty list to indicate no results
    else:
        search_results = None  # No search performed
    
    context = {
        'active_tasks': active_tasks,
        'completed_tasks': completed_tasks,
        'form': form,
        'search_results': search_results,
        'query': query,  # To maintain the search term in the input field
        'task_id': task_id,  # For identifying if it's an edit action
    }
    
    return render(request, 'tasks/dashboard.html', context)

def delete_task(request, task_id):
    task = get_object_or_404(Task, id=task_id, user=request.user)
    if request.method == 'POST':
        task.delete()
        return redirect('dashboard')
    
    return render(request, 'tasks/task_confirm_delete.html', {'task': task})

@login_required
def mark_as_complete(request, task_id):
    # Get the task and ensure it belongs to the logged-in user
    task = get_object_or_404(Task, id=task_id, user=request.user)
    # Update the task's status to "Completed" (status=2)
    task.status = 2  # 2 corresponds to "Completed"
    task.save()
    # Redirect back to the dashboard
    return HttpResponseRedirect(reverse('dashboard'))

@login_required
def change_priority(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        new_priority = request.POST.get('priority')
        if new_priority in ['High', 'Normal', 'Low']:
            task.priority = new_priority
            task.save()
    return redirect('dashboard')

@login_required
def change_status(request, task_id):
    if request.method == 'POST':
        task = get_object_or_404(Task, id=task_id, user=request.user)
        new_status = request.POST.get('status')
        if new_status in ['0', '1', '2']:
            task.status = int(new_status)
            task.save()
    return redirect('dashboard')