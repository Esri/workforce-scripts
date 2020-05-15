# Scheduling Workforce Scripts in Linux / macOS

Users may want to have the scripts in this repository run at certain frequencies. For example, a user may want to 
run `delete_assignments.py` once a day to delete all completed assignments, or run `reset_stale_workers.py`. once a
week to reset workers that aren't working to the correct status.

On Windows, we recommend using Windows Task Scheduler for this action. See our blog post here [here](https://community.esri.com/groups/workforce-for-arcgis/blog/2020/05/14/schedule-tasks-for-workforce)
for more on how to set that up.

On Linux and Mac, you have two options: either use `crontab`, a [job scheduler](http://man7.org/linux/man-pages/man5/crontab.5.html) 
built into Unix, or refactor your script to use the `schedule` library from Python. Crontab has the advantage of running
in the background, while `schedule` may be easier to configure. There are a variety of online resources on configuring
a Cron job to run a Python script periodically.

However, if you want a barebones way of scheduling tasks (in any platform), you can use Python's
`schedule` library to schedule any task you'd wish. It will require very minor adaptation to the script on your part.

Take the example of `delete_assignments.py`. To schedule `delete_assignments` to run every 2 hours, for example,
you should:

1. Install `schedule` into your Conda package by running `pip install schedule` on the command line
2. Then, add the `schedule` and `time` modules at the top of your chosen script:
    ```python
    import schedule
    import time
    ```
3. Then, locate the line where the scripts attempts to run the `main` function in a try/except block at the end of the
file. 
    ```python
    try:
       main(args)
    except Exception as e:
       logging.getLogger().critical("Exception detected, script exiting")
    ```
4. Replace `main(args)` with your job scheduling code. The code block below schedules the function `main` to run with
the arguments `args` (which were passed in by you at command line) every two hours.
    ```python
    try:
        schedule.every(2).hours.do(main, args)
        while True:
            schedule.run_pending()
            time.sleep(1)
    except Exception as e:
       logging.getLogger().critical("Exception detected, script exiting")
    ```
5. To avoid subsequent jobs logging multiple times, remove the file handlers by adding to the final line of the main
function - i.e. immediately after `logger.info("Completed!")` the code:
    ```python
    logger.removeHandler(sh)
    # if you provided a log file when running the script, include this next line as well
    logger.removeHandler(rh)
    ```
6. Run your script as you would normally and leave running on a machine. Script will not exit and run periodically until
you manually quit.    