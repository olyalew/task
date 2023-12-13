import flet as ft
import flet
from flet import *
from datetime import datetime
import sqlite3

class Database:
    def ConnectToDatabase():
        try:
            db = sqlite3.connect('todo.db')
            c = db.cursor()
            c.execute("CREATE TABLE if not exists tasks (id INTEGER PRIMARY KEY, Task VARCHAR(255) NOT NULL, Date VARCHAR(255) NOT NULL)")
            return db
        except Exception as e:
            print(e)

    def ReadDatabase(db):
        c = db.cursor()
        c.execute("SELECT Task, Date FROM tasks")
        records = c.fetchall()
        return records

    def InsertDatabase(db, values):
        c = db.cursor()
        c.execute("INSERT INTO tasks (Task, Date) VALUES (?,?)", values)
        db.commit()

    def DeleteDatabase(db, value):
        c = db.cursor()
        c.execute("DELETE FROM tasks WHERE Task=?", value)
        db.commit()

    def UpdateDatabase(db, value):
        c = db.cursor()
        c.execute("UPDATE tasks SET Task=? WHERE Task=?", value)
        db.commit()

# form class first so we can get some data
class FormContainer(UserControl):
    # at these points, we can pass in a function from the main() so we can expand.
    # minimize the form
    # go back to FormContainer() and add an argument as such
    def __init__(self, func):
        self.func = func
        super().__init__()

    def build(self):
        return Container(
            width=280,
            height=0,
            bgcolor="#151819",
            opacity=1,
            border_radius=30,
            margin=margin.only(left=-20, right=-20),
            animate=animation.Animation(400, "decelerate"),
            animate_opacity=200,
            padding=padding.only(top=45, bottom=45),
            content=Column(
                horizontal_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    TextField(
                        height=48,
                        width=255,
                        filled=True,
                        color="white",
                        bgcolor="#070606",
                        text_size=12,
                        border_radius=10,
                        border_color="#5C6373",
                        hint_text="Description...",
                        hint_style=TextStyle(size=11, color="#5C6373"),
                    ),
                    IconButton(
                        content=Text('Add Task', color="black", weight="normal"),
                        width=180,
                        height=44,
                        on_click=self.func,
                        style=ButtonStyle(
                            bgcolor={"": '#4CFF89'},
                            shape={
                                "": RoundedRectangleBorder(radius=8),
                            },
                        ),
                    ),
                ],
            ),
        )

# we need a class to generate a task when user adds one
class CreateTask(UserControl):
    def __init__(self, task: str, date: str, func1, func2):
        self.task = task
        self.date = date
        self.func1 = func1
        self.func2 = func2
        super().__init__()

    def TaskDeleteEdit(self, name, color, func):
        return IconButton(
            icon=name,
            width=30,
            icon_size=18,
            icon_color=color,
            opacity=0,
            animate_opacity=200,
            on_click=lambda e: func(self.GetContainerInstance()),
        )

    def GetContainerInstance(self):
        return self

    def ShowIcons(self, e):
        if e.data == "true":
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity,
            ) = (1, 1)
            e.control.content.update()
        else:
            (
                e.control.content.controls[1].controls[0].opacity,
                e.control.content.controls[1].controls[1].opacity,
            ) = (0, 0)
            e.control.content.update()

    def build(self):
        return Container(
            width=280,
            height=60,
            border=border.all(0.85, 'white54'),
            border_radius=8,
            on_hover=lambda e: self.ShowIcons(e),
            clip_behavior=ClipBehavior.HARD_EDGE,
            padding=10,
            content=Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    Column(
                        spacing=1,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            Text(value=self.task, size=10),
                            Text(value=self.date, size=9, color='white54'),
                        ],
                    ),
                    # Icons Delete and Edit
                    Row(
                        spacing=0,
                        alignment=MainAxisAlignment.CENTER,
                        controls=[
                            self.TaskDeleteEdit(icons.DELETE_ROUNDED, 'red500', self.func1),
                            self.TaskDeleteEdit(icons.EDIT_ROUNDED, 'white70', self.func2),
                        ]
                    )
                ],
            ),
        )

def main(page: Page):
    page.horizontal_alignment = "center"
    page.vertical_alignment = "center"

    def AddTaskToScreen(e):
        # now, every time then user adds a task, we need to fetch the data and output it to the main column
        # there are 2 data we need: the task and the date
        dateTime = datetime.now().strftime("%b %d, %Y  %I:%M")

        db = Database.ConnectToDatabase()
        Database.InsertDatabase(db, (form.content.controls[0].value, dateTime))
        db.close()



        # now recall that we set the form container to form variable. we can use this now to see if there's any
        # content in the textfield
        if form.content.controls[0].value:
            _main_column_.controls.append(
                CreateTask(
                    form.content.controls[0].value,
                    dateTime,
                    DeleteFunction,
                    UpdateFunction,
                )
            )
            _main_column_.update()

            CreateToDoTask(e)
        else:
            db.close()
            pass

    def DeleteFunction(e):
        db = Database.ConnectToDatabase()
        Database.DeleteDatabase(
            db, (e.controls[0].content.controls[0].controls[0].value,)
        )
        db.close()

        _main_column_.controls.remove(e)
        _main_column_.update()

    def UpdateFunction(e):
        form.height, form.opacity = 200, 1
        (
            form.content.controls[0].value,
            form.content.controls[1].content.value,
            form.content.controls[1].on_click
        ) = (
            e.controls[0].content.controls[0].controls[0].value,
            "Update",
            lambda _: FinalizeUpdate(e),
        )
        form.update()

    def FinalizeUpdate(e):
        db = Database.ConnectToDatabase()
        Database.UpdateDatabase(
            db,
            (
                form.content.controls[0].value,
                e.controls[0].content.controls[0].controls[0].value,
            ),
        )

        e.controls[0].content.controls[0].controls[0].value = form.content.controls[0].value
        e.controls[0].content.update()
        CreateToDoTask(e)

    # function to show/hide form container
    def CreateToDoTask(e):
        # when we click the ADD icon button ...
        if form.height != 200:
            form.height, form.opacity = 200, 1
            form.update()
        else:
            form.height, form.opacity = 80, 0
            form.content.controls[0].value = None
            form.content.controls[1].content.value = "Add Text"
            form.content.controls[1].on_click = lambda e: AddTaskToScreen(e)
            form.update()

    _main_column_ = Column(
        scroll="hidden",
        expand=True,
        alignment=MainAxisAlignment.START,
        controls=[
            Row(
                alignment=MainAxisAlignment.SPACE_BETWEEN,
                controls=[
                    # some title stuff
                    Text("To-do Tasks", size=18, weight="bold"),
                    IconButton(
                        icons.ADD_CIRCLE_ROUNDED,
                        icon_size=18,
                        on_click=lambda e: CreateToDoTask(e),
                    ),
                ],
            ),
            Divider(height=8, color="white24"),
        ],
    )

    # set up some bg and main container
    # the general UI will copy that of a mobile app
    page.add(
        # this is just a bg container
        Container(
            width=280,
            height=550,
            bgcolor="#6F6F70",
            border_radius=45,
            alignment=alignment.center,
            content=Row(
                alignment=MainAxisAlignment.CENTER,
                vertical_alignment=CrossAxisAlignment.CENTER,
                controls=[
                    # Main container
                    Container(
                        width=270, height=540, bgcolor="#070606",
                        border_radius=40,
                        padding=padding.only(top=35, left=20, right=20),
                        clip_behavior=ClipBehavior.HARD_EDGE,  # clip content to container
                        content=Column(
                            alignment=MainAxisAlignment.CENTER,
                            expand=True,
                            controls=[
                                # main column here
                                _main_column_,
                                # form class here
                                FormContainer(lambda e: AddTaskToScreen(e)),
                            ]
                        )
                    )
                ]
            )
        )
    )
    page.update()

    # the form container index is as follows. We can set the long element index as a variable, so it can be called
    # faster and easier.
    form = page.controls[0].content.controls[0].content.controls[1].controls[0]
    # now we can call form whenever we want to do something with it
    db = Database.ConnectToDatabase()

    for task in Database.ReadDatabase(db)[::-1]:
        _main_column_.controls.append(
            CreateTask(
                task[0],
                task[1],
                DeleteFunction,
                UpdateFunction,
            )
        )
    _main_column_.update()

if __name__ == "__main__":
    flet.app(target=main)
