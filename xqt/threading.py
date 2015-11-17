from xqt import QtCore

class TaskInProgress(StandardError):
    def __init__(self, task):
        self.task = task
        msg = '{0} is already running.'.format(getattr(task, 'name', task.__name__))
        super(TaskInProgress, self).__init__(msg)


class Task(QtCore.QObject):
    started = QtCore.Signal()               # Emitted when the task starts
    succeeded = QtCore.Signal(object)       # Successful result of the task
    errored = QtCore.Signal(StandardError)  # Error that occurred during the task
    finished = QtCore.Signal()              # Emitted when the task finishes either way

    def __init__(self, runner, args, kwargs, thread=None):
        super(Task, self).__init__()

        # move this task to its own thread
        self.moveToThread(thread or self.globalThread())

        # define custom properties
        self.__runningLock = QtCore.QReadWriteLock()
        self.__running = False
        self.__runner = runner
        self.__args = args
        self.__kwargs = kwargs
        self.__exception = None
        self.__result = None
        self.__finished = False

    def done(self, callback):
        """
        Chains the given callback togehter as the slot to be called when this task is finished,
        regardless of if it is successful or a failure.

        :usage

            |>>> task = Task(runner).done(callback).start()

        :param callback: <callable>

        :return: <Task>
        """

    def isFinished(self):
        """
        Returns whether or not this task has completed running.

        :return: <bool>
        """
        with QtCore.QReadLocker(self.__runningLock):
            return self.__finished

    def isRunning(self):
        """
        Returns whether or not this task is currently running.

        :return: <bool>
        """
        with QtCore.QReadLocker(self.__runningLock):
            return self.__running

    def exception(self):
        """
        Returns the exception that was raised during the execution of this task.

        :return: <StandardError> || None
        """
        return self.__exception

    def error(self, callback):
        """
        Chains the given callback together as the slot to be called when this task errors out.

        :usage

                |>>> task = Task(runner).error(callback).start()

        :param  callback: <callable>

        :return: <Task>
        """
        self.errored.connect(callback, QtCore.Qt.QueuedConnection)
        return self

    def success(self, callback):
        """
        Chains the given callback together as the slot to be called when this task finishes successfully.

        :param callback:
        :return:
        """
        self.succeeded.connect(callback, QtCore.Qt.QueuedConnection)
        return self

    def result(self):
        """
        Returns the result that was received when the task runner is finished successfully.

        :return: <variant>
        """
        return self.__result

    def run(self):
        """
        Runs this task's method.  When the method finishes, the finished signal will be emitted, and
        if an error occurs during execution, the errored signal will be emitted.  Otherwise, the succeeded
        signal will be emitted.
        """
        self.started.emit()
        with QtCore.QWriteLocker(self.__runningLock):
            self.__running = True

        try:
            self.__result = self.__runner(*self.__args, **self.__kwargs)
            self.succeeded.emit(self.__result if self.__result is not None else QtCore.THREADSAFE_NONE)
        except StandardError as err:
            self.__exception = err
            self.errored.emit(err)
        finally:
            with QtCore.QWriteLocker(self.__runningLock):
                self.__finished = True
                self.__running = False
            self.finished.emit()

    def start(self):
        """
        Kicks off this task by emitting a timer event to this task's run method.

        :return: <Task>
        """
        QtCore.QTimer.singleShot(0, self.run)
        return self

    def wait(self):
        """
        Spins an event loop waiting for this task to finish.  This will allow you to call a task
        as a synchronous call while not blocking the main UI event loop.

        :warning        Processing events is dangerous and should be used sparingly!  This
                        is mostly helpful for debugging, but should not be used for production code.

        :return: <variant>
        """
        app = QtCore.QCoreApplication.instance()
        if app.thread() == QtCore.QThread.currentThread():
            loop = app
        else:
            loop = QtCore.QEventLoop()

        while not self.isFinished() and not app.closingDown():
            loop.processEvents()

        with QtCore.QWriteLocker(self.__runningLock):
            if self.__exception is not None:
                raise self.__exception
            else:
                return self.__result

    @classmethod
    def cleanupThread(cls):
        """
        Cleans up the thread that was created for this task type.
        """
        thread = getattr(cls, '_{0}__thread'.format(cls.__name__), None)
        if thread is not None:
            setattr(cls, '_{0}__thread'.format(cls.__name__), None)
            thread.quit()
            thread.wait(1000)

    @classmethod
    def globalThread(cls):
        """
        Creates a global thread for this task's class type.

        :return: <QtCore.QThread>
        """
        thread = getattr(cls, '_{0}__thread'.format(cls.__name__), None)
        if thread is None:
            app = QtCore.QCoreApplication.instance()
            thread = QtCore.QThread()
            app.aboutToQuit.connect(cls.cleanupThread)
            thread.start()
            setattr(cls, '_{0}__thread'.format(cls.__name__), thread)
        return thread

    @classmethod
    def runner(cls, method):
        """
        Decorator to easily create a task by wrapping any method.  The wrapped method will
        not return a default response, but a Task object based on the called class type.  It will
        also automatically

        :usage

            |from tbx.threading import Task
            |
            |@Task.runner
            |def do_something(a, b):
            |   return a * b
            |
            |do_something(10, 2).success(def show(result): print result)

        :param method: <callable>

        :return: <callable>
        """
        def wrapper(*args, **kwargs):
            return cls(method, args, kwargs).start()
        return wrapper


class TaskQueue(QtCore.QObject):
    startRequested = QtCore.Signal()

    started = QtCore.Signal(QtCore.QObject)
    succeeded = QtCore.Signal(QtCore.QObject, object)
    errored = QtCore.Signal(QtCore.QObject, StandardError)
    finished = QtCore.Signal(QtCore.QObject)

    def __init__(self, taskType=None, thread=None, parent=None):
        super(TaskQueue, self).__init__(parent)

        # define custom properties
        self.__taskType = taskType or Task
        self.__taskThread = thread
        self.__queueLock = QtCore.QReadWriteLock()
        self.__queue = []
        self.__current = None

    def currentTask(self):
        """
        Returns the currently processing task for this queue.

        :return: <tbx.threading.Task> || None
        """
        with QtCore.QReadLocker(self.__queueLock):
            return self.__current

    def finish(self):
        """
        Finishes out the current task and then attempts to start the next one.  This method is called
        when a task finishes out its previous execution.
        :return:
        """
        task = self.sender()
        with QtCore.QWriteLocker(self.__queueLock):
            if task != self.__current:
                return
            else:
                self.__current = None
                self.startRequested.disconnect(task.run)
                task.finished.disconnect(self.finish)

        self.finished.emit(task)
        return self.start()

    def isEmpty(self):
        """
        Returns whether or not this queue is currently empty.

        :return: <bool>
        """
        with QtCore.QReadLocker(self.__queueLock):
            return len(self.__queue) == 0

    def isRunning(self):
        """
        Returns whether or not this queue currently is running a task.

        :return: <bool>
        """
        with QtCore.QReadLocker(self.__queueLock):
            return self.__current is not None

    def push(self, task):
        """
        Pushes the task into the end of this task queue for processing.

        :param task: <tbx.threading.Task>

        :return: <tbx.threading.Task>
        """
        with QtCore.QWriteLocker(self.__queueLock):
            # create connections for the task
            task.finished.connect(self.finish, QtCore.Qt.QueuedConnection)
            task.started.connect(self.relayStarted, QtCore.Qt.QueuedConnection)
            task.succeeded.connect(self.relaySucceeded, QtCore.Qt.QueuedConnection)
            task.errored.connect(self.relayErrored, QtCore.Qt.QueuedConnection)

            # queue it up to process
            self.__queue.append(task)

        try:
            self.start()
        except TaskInProgress:
            pass

        return task

    def relayErrored(self, err):
        """
        Passes along the errored signal from the currently executed task.  This method is triggered internally
        from the task queue.

        :param err: <StandardError>
        """
        task = self.sender()
        with QtCore.QReadLocker(self.__queueLock):
            emit = task == self.__current

        if emit:
            self.errored.emit(task, err)

    def relayStarted(self):
        """
        Passes along the started signal from the currently executed task.  This method is triggered internally
        from the task queue.
        """
        task = self.sender()
        with QtCore.QReadLocker(self.__queueLock):
            emit = task == self.__current

        if emit:
            self.started.emit(task)

    def relaySucceeded(self, result):
        """
        Passes along the succeeded signal from the currently executed task.  This method is triggered internally
        from the task queue.

        :param result: <variant>
        """
        task = self.sender()
        with QtCore.QReadLocker(self.__queueLock):
            emit = task == self.__current

        if emit:
            self.succeeded.emit(task, result)

    def start(self):
        """
        Starts the next task within this task queue, if one is available.  If there is currently a task
        running, then it will raise a TaskInProgress error.

        :return:  <tbx.threading.Task> || None
        """
        with QtCore.QWriteLocker(self.__queueLock):
            if self.__current:  # already have a task running
                raise TaskInProgress(self.__current)
            elif not self.__queue:  # don't have another task to queue up
                return
            else:
                self.__current = self.__queue.pop()
                QtCore.QTimer.singleShot(0, self.__current.run)
                return self.__current

    def setTaskThread(self, thread):
        """
        Assigns the default thread to move the tasks being processed by this queue to.  If not specified,
        then the thread of the class type of the Task associated with this queue will be used.

        :param thread:  <QtCore.QThread>
        """
        self.__taskThread = thread

    def task(self, method):
        """
        Decorator for easily adding callable methods and functions to this task queue.  When the decorated
        method is called, then a new task is created and pushed into the task's queue.

        :usage

            |>>> queue = TaskQueue()
            |>>> @queue.task
            |... def do_something(a, b):
            |...     return a * b

        :param      method | <callable>

        :return     <callable>
        """
        def wrapper(*args, **kwargs):
            task = self.__taskType(method, args, kwargs, thread=self.taskThread())
            return self.push(task)
        return wrapper

    def taskThread(self):
        """
        Returns the default thread to move the tasks being processed by this queue to.  If not specified,
        then the thread of the class type of the Task associated with this queue will be used.

        :return     <QtCore.QThread> || None
        """
        return self.__taskThread

    def wait(self):
        """
        Waits for the currently running task to finish by spinning the event loop.

        :warning    This is not recommended as spinning the event loop is dangerous and can cause
                    hangs.

        :return:    <variant>
        """
        with QtCore.QReadLocker(self.__queueLock):
            task = self.__current

        if task:
            return task.wait()
        else:
            return None
