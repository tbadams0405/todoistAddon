#This script will add a given label to all of the tasks in a given project and its 
#subprojects. 


import todoist

api_key = raw_input("enter api key: ")
main_project_name = raw_input("enter project name - case sensitive: ")
label_name = raw_input("enter label name - this one's case insensitive: ")

api = todoist.TodoistAPI(api_key) #api key needed for todoist

print('Working...')
#determines if a task belongs to any project in a list of given projects
def taskInProject(task, project_list):
	for proj in project_list:
		if task[u'project_id'] == proj[u'id']:
			return True


#Sorts Projects By Item Order, ascending
#project_universe must be a list of only projects
def sortProjectsByItemOrder(project_universe):
	for i in range(1, len(project_universe)):
		j = i
		while j > 0 and project_universe[j][u'item_order'] < project_universe[j-1][u'item_order']:
			project_universe[j], project_universe[j-1] = project_universe[j-1], project_universe[j]
			j -= 1



###Get dictionary defining main work project
projects = api.sync(resource_types=['projects']) #gets dictionary of projects and associated data
my_projects=[]
# uses generator expression. http://stackoverflow.com/questions/8653516/python-list-of-dictionaries-search
my_projects.append(next((item for item in projects[u'Projects'] if item[u'name'] == main_project_name), None)) #gets main project
main_project_id = my_projects[0][u'id']
main_project_item_order = my_projects[0][u'item_order'] #placement in the projects list

###Get subprojects of main_work_project
sortProjectsByItemOrder(projects[u'Projects'])
for j in range(main_project_item_order+1, len(projects[u'Projects'])):
	if projects[u'Projects'][j][u'indent'] == my_projects[0][u'indent']:
		break
	else:
		my_projects.append(projects[u'Projects'][j])


###Get @work label id
labels = api.sync(resource_types=['labels'])
my_label = next((item for item in labels[u'Labels'] if item[u'name'] == label_name), None)
my_label_id = my_label[u'id']

###Get tasks in my_projects
tasks = api.sync(resource_types=['items'])
tasks_in_my_projects = []
for item in tasks[u'Items']:
	if taskInProject(item, my_projects):
		tasks_in_my_projects.append(item)

###Add @work label to tasks in main work project
for item in tasks_in_my_projects:
	task = api.items.get_by_id(item[u'id'])
	task_labels = task[u'labels'] #don't want to overwrite current labels of work project
	task_labels.append(my_label_id)
	task.update(labels=task_labels)

print('\nCommitting changes...')	
api.commit()
print('\nDone!')