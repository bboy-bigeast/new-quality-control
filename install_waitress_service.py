#!/usr/bin/env python
"""
Windows service installation script for Waitress deployment
Run with administrator privileges:
python install_waitress_service.py install
python install_waitress_service.py start
python install_waitress_service.py stop
python install_waitress_service.py remove
"""

import os
import sys
import time
import win32serviceutil
import win32service
import win32event
import servicemanager
import subprocess
import threading

class QualityControlService(win32serviceutil.ServiceFramework):
    """Windows Service for Quality Control Application"""
    
    _svc_name_ = "QualityControlWaitress"
    _svc_display_name_ = "Quality Control Waitress Server"
    _svc_description_ = "Django Quality Control application served with Waitress"
    
    def __init__(self, args):
        win32serviceutil.ServiceFramework.__init__(self, args)
        self.hWaitStop = win32event.CreateEvent(None, 0, 0, None)
        self.process = None
        
    def SvcStop(self):
        self.ReportServiceStatus(win32service.SERVICE_STOP_PENDING)
        if self.process:
            self.process.terminate()
        win32event.SetEvent(self.hWaitStop)
        
    def SvcDoRun(self):
        servicemanager.LogMsg(servicemanager.EVENTLOG_INFORMATION_TYPE,
                             servicemanager.PYS_SERVICE_STARTED,
                             (self._svc_name_, ''))
        self.main()
        
    def main(self):
        """Main service method that runs the Waitress server"""
        try:
            # Change to the project directory
            project_dir = os.path.dirname(os.path.abspath(__file__))
            os.chdir(project_dir)
            
            # Start Waitress server
            self.process = subprocess.Popen([
                sys.executable, 
                "deploy_waitress_production.py"
            ], stdout=subprocess.PIPE, stderr=subprocess.PIPE, text=True)
            
            servicemanager.LogInfoMsg("Quality Control Waitress service started successfully")
            
            # Wait for the process to complete or service stop
            while True:
                if win32event.WaitForSingleObject(self.hWaitStop, 1000) == win32event.WAIT_OBJECT_0:
                    break
                    
                # Check if process is still running
                if self.process.poll() is not None:
                    servicemanager.LogErrorMsg("Waitress process stopped unexpectedly")
                    break
                    
        except Exception as e:
            servicemanager.LogErrorMsg(f"Service error: {str(e)}")
        finally:
            if self.process:
                self.process.terminate()

def install_service():
    """Install the service"""
    try:
        win32serviceutil.InstallService(
            None,
            'QualityControlWaitress',
            'Quality Control Waitress Server',
            description='Django Quality Control application served with Waitress',
            startType=win32service.SERVICE_AUTO_START
        )
        print("✅ Service installed successfully!")
        print("Use 'python install_waitress_service.py start' to start the service")
    except Exception as e:
        print(f"❌ Error installing service: {e}")

def main():
    if len(sys.argv) == 1:
        print("Usage: python install_waitress_service.py [install|start|stop|remove]")
        print("Options:")
        print("  install - Install the service")
        print("  start   - Start the service")
        print("  stop    - Stop the service")
        print("  remove  - Remove the service")
        print("  debug   - Run in console mode for debugging")
        return
    
    if sys.argv[1] == 'debug':
        # Run in console mode for debugging
        service = QualityControlService(['QualityControlWaitress'])
        service.main()
    else:
        win32serviceutil.HandleCommandLine(QualityControlService)

if __name__ == '__main__':
    main()
