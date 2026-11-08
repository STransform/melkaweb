from django.views import View
from django.contrib import messages
from django.core.mail import EmailMultiAlternatives
from django.contrib.auth.mixins import LoginRequiredMixin
from django.contrib.auth.decorators import login_required
from django.shortcuts import render, redirect,get_object_or_404


from .models import Task, Comment
from .forms import CommentForm, TaskForm

class ListTasks(LoginRequiredMixin, View):
    def get(self, *args, **kwargs):
        status = ['New', 'Inprogress', 'Completed', 'Overdue']
        user = self.request.user
        type = self.kwargs.get('type')
        if type == 'Assigned':
            tasks = user.assigned_tasks.all()
        elif type == 'Monitoring':
            tasks = user.monitoring_tasks.all()
        elif type == 'My':
            tasks = Task.objects.filter(created_by = user )
        elif type == 'All':
            tasks = Task.objects.all()
        context = {
            'tasks': tasks, 'form':TaskForm(), 'type':type, 'status':status
        }
        return render(self.request, 'task-list-view.html', context)
    

class AssignTask(LoginRequiredMixin, View):
    def get(self, request):
        return redirect('task_list_view', type="All")
    
    def post(self, request):
        form = TaskForm(request.POST)
        if form.is_valid():
            task = form.save(commit=False)
            task.created_by = request.user
            task.save()
            form.save_m2m()
            messages.success(request, "Task assigned successfully!")
            
            # send email for assigned users
            for u in task.assigned_to.all():
                msg = f"You have been assigned on a new task named: {task.task_name}."
                email = u.email
                e = EmailMultiAlternatives(f"Assigned on new task : {task.task_name}", msg,
                                           from_email="Finance Bureau",
                                           to=[str(email)], )
                m = e.send()
            
            messages.success(request, "Notification email sent to assigned users!")
            
            # send email for the monitors
            for u in task.monitoring.all():
                msg = f"You have been assigned to monitor a new task named: {task.task_name}."
                email = u.email
                e = EmailMultiAlternatives(f"Assigned as a monitor for a new task : {task.task_name}", msg,
                                           from_email="Finance Bureau",
                                           to=[str(email)], )
                m = e.send()
            
            messages.success(request, "Notification email sent to users assigned as monitors!")
            return redirect('task_list_view',type='All')   
            
        messages.error(request, f"Invalid data detected! \n {form.errors.as_text()}")
        return redirect('task_list_view', type='My')



def delete_task(request, task_id):
    try:
        task = get_object_or_404(Task, id=task_id)
        task.delete() 
        messages.success(request, "Task deleted successfully!")
    except Exception as e:
        messages.error(request, str(e))
    return redirect('task_list_view', type='My')


class TaskDetailsView(LoginRequiredMixin, View):
    def get(self, request, task_id):
        user = self.request.user
        task = get_object_or_404(Task, id=task_id)
        # A user can update a task if he is the creator and not an assigned member.
        can_edit = True if task.created_by == user else False
        context = {
            'task': task,
            'form':TaskForm(instance=task),
            'can_edit':can_edit,
            'comments':task.comments.filter(parent_comment= None)
        }

        return render(request, 'task_details_admin.html', context)

    def post(self, request, task_id):
        task = Task.objects.get(id=task_id)
        form = TaskForm(instance=task, data=request.POST)

        if form.is_valid():
            task = form.save(commit=False)
            task.save()
            form.save_m2m()
            messages.success(request, "Task updated successfully!")
            
            # send email for assigner user
           
            updated_by= request.user
            msg = f"A task named: {task.task_name}. is updated by {updated_by}."
            email = task.created_by.email
            e = EmailMultiAlternatives(f"Updated task : {task.task_name}", msg,
                                        from_email="Finance Bureau",
                                        to=[str(email)], )
            m = e.send()
            
            messages.success(request, "Notification email sent to person who assigned the task!")
            
            return redirect('task_details', task_id)   
            
        print(form.errors)
        messages.error(request, "Invalid data detected. Please recheck your inputs!")
        return redirect('task_details', task_id=id)



def get_key_tasks(task):
    return task.key_tasks.split('\n') if task.key_tasks else []


@login_required
def add_comment(request, task_id):
    task = Task.objects.get(id=task_id)
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            user_profile = request.user
            content = form.cleaned_data['comment_content']
            Comment.objects.create(task=task, user=user_profile, content=content)
            messages.success(request, "Successfully commented on task.")
            return redirect('task_details', task_id=task.id)  # Redirect to the same page after posting comment
    
    return redirect('task_details', task_id=task.id)
    # return render(request, 'task_details_admin.html', context)


@login_required
def reply_comment(request, comment_id):
    comment = Comment.objects.get(id=comment_id)
    task_id = comment.task.id  # Get the task id associated with the comment
    task = comment.task  # Retrieve the task object
    if request.method == 'POST':
        form = CommentForm(request.POST)
        if form.is_valid():
            user_profile = request.user  # Retrieve the UserProfile object associated with the authenticated user
            content = form.cleaned_data['comment_content']
            # Assuming you have a field to store the parent comment in your Comment model
            reply = Comment.objects.create(task=comment.task, user=user_profile, content=content, parent_comment=comment)
            return redirect('add_comment', task_id=task_id)  # Redirect to task detail page
    else:
        form = CommentForm()
    context = {
        'form': form,
        'task': task,  # Pass the task object to the template context
    }
    return render(request, 'task_details_admin.html', context)
