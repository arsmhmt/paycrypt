@echo off
REM Batch script to delete unused template files

del "app\templates\client\dashboard_enhanced.html"
del "app\templates\admin\clients2.html"
del "app\templates\admin\clients_debug.html"
del "app\templates\admin\analytics_test.html"
del "app\templates\admin\analytics_new.html"
del "app\templates\admin\analytics_old.html"

echo Unused template files deleted.
