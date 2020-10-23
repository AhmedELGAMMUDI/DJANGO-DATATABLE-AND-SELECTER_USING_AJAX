
@login_required
@permission_required("college.add_classes", raise_exception=True)
@permission_required("college.change_classes", raise_exception=True)
@permission_required("college.delete_classes", raise_exception=True)
@permission_required("college.view_classes", raise_exception=True)
@transaction.atomic
def Assign_Teacher_Classes(request):
    Class_List = Classes.objects.all() 
    Class_Object = None
    Course_in_Class = None
    Class_Student_List = None
    Teacher_Class_List = None
    Course_uuid = request.GET.get('Course_uuid')
    Course_Object = Courses.objects.filter(uuid = Course_uuid).first()
    Course_Teachers =  None
    Non_Selected_Students = None
    
    if request.method == 'GET':
        class_uuid = request.GET.get('class_uuid')
        if class_uuid:
            Class_Object = Classes.objects.get(uuid=class_uuid)#Seçilen SInıf
            Course_in_Class = Courses.objects.filter(semester = get_last_semester(),class_year=Class_Object.class_year,class_branch=Class_Object.class_branch) #Seçilen sınıfa atanmış dersler (sınıf yılına göre)
            Class_Student_List = AssignStudentCourseClasses.objects.filter(semester=get_last_semester(), student_class=Class_Object) # Seçilen Sınıfın Tüm Öğrencileri
            Teacher_Class_List = AssignTeacherCourseClasses.objects.filter(semester=get_last_semester(), teacher_class=Class_Object) # Seçilen Sınıfa Atanmış Öğretmenler (Ders ve öğrencileri ile birlikte)
                
            if Course_Object:
                Course_Teachers = Get_Course_Teachers(Course_Object,Class_Object) #Seçilen Kursun, Seçilen sınıf için öğretmenleri
                
                Course_Student = [] # Seçilen Dersin öğretmenleri tarafından seçilen Öğrenciler
                for class_techer in Teacher_Class_List:
                    if class_techer.teacher_course == Course_Object:
                        for student in class_techer.teacher_students.all():
                            Course_Student.append(student)

                course_in_student = Get_Course_Student(Course_Object) #Seçilen Dersi Alan Öğrenciler
                
                Non_Selected_Students = [] # Seçilen Dersi Almayan Öğrenciler
                for Class_Student in Class_Student_List:
                    if not Class_Student.student in Course_Student and Class_Student.student in course_in_student:
                        Non_Selected_Students.append(Class_Student.student)
                
                if not course_in_student:
                    messages.add_message(request, messages.WARNING, _("This course is Not Assigned to Students of this Class"))                  
                    return redirect(reverse('Assign-Teacher-Classes') + '?class_uuid=' + str(class_uuid)) 
                elif not Non_Selected_Students:
                    messages.add_message(request, messages.WARNING, _("All Student Assign to Teacher for This Course"))  
                    return redirect(reverse('Assign-Teacher-Classes') + '?class_uuid=' + str(class_uuid))


    elif request.method == 'POST':
        class_uuid = request.POST.get('class_uuid')
        remove_uuid = request.POST.get('remove_uuid')
        edit_uuid = request.POST.get('edit_uuid')
        action= request.POST.get('action')

               
        if remove_uuid: #DELETE
            try:
                AssignTeacherCourseClasses.objects.filter(uuid=remove_uuid).delete()
                messages.add_message(request, messages.INFO, _("Teacher Unassign to Class Operation Successfully Completed"))
            except ProtectedError as err:
                    messages.add_message(request, messages.ERROR,str(err) + _("Please contact system administrator with above warning."))
            except Exception as err:
                    messages.add_message(request, messages.ERROR, str(err) + _("Please contact system administrator with above warning."))

        elif action == 'save' or action == 'update' :   #CREATE or UPDATE
            if edit_uuid is None:  
                form = AssignTeacherCourseClassesForm(request.POST, request.FILES or None) #CREATE
            else:
                instance = get_object_or_404(AssignTeacherCourseClasses, uuid=edit_uuid)
                form = AssignTeacherCourseClassesForm(request.POST or None, request.FILES or None, instance=instance)#UPDATE
            if form.is_valid():
                teacher_form=form.save(commit=False)
                teacher_form.semester = get_last_semester()

                try:
                    teacher_form.save()
                    form.save_m2m()
                except Exception as err:
                    messages.add_message(request, messages.WARNING, _("%s person has already been assigned to %s course, you can assign students by using the edit button") % (str(teacher_form.teacher.name)+" "+str(teacher_form.teacher.surname),_(teacher_form.teacher_course.course_code)))

            else:
                messages.add_message(request, messages.ERROR, str(form.errors))
    
        return redirect(reverse('Assign-Teacher-Classes') + '?class_uuid=' + str(class_uuid))

    return render(request, 'Assign-Teacher-Classes.html',{'Class_List':Class_List,
                                                                                                            'Class_Object':Class_Object,
                                                                                                            'Course_in_Class':Course_in_Class,
                                                                                                            'Course_Object':Course_Object,
                                                                                                            'Course_Teachers':Course_Teachers,
                                                                                                            'Class_Student_List':Class_Student_List,
                                                                                                            'Non_Selected_Students':Non_Selected_Students,
                                                                                                            'Teacher_Class_List':Teacher_Class_List,})
