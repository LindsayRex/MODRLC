# -*- coding: utf-8 -*-
'''
This script demonstrates a minimalistic example of testing a feedback controller
using the scenario options with the prototype test case called "testcase1".

'''

import sys
import pathlib
# Add BOPTEST repository to PYTHONPATH for this example
sys.path.insert(0, str(pathlib.Path(__file__).absolute().parents[2]))

def run(plot=False):
    '''This is the main script.

    Parameters
    ----------
    plot : boolean
        True to plot result at end.
        Default is True.

    Returns
    -------
    kpi : dict
        Dictionary containing KPI values at end of test.

    '''

    # GENERAL PACKAGE IMPORT
    # -----------------------------------------------------------------------------
    import requests
    import numpy as np
    # -----------------------------------------------------------------------------
    # TEST CONTROLLER IMPORT
    # -----------------------------------------------------------------------------
    from examples.python.controllers import pid
    # -----------------------------------------------------------------------------
    # SET TEST PARAMETERS
    # -----------------------------------------------------------------------------
    # Set URL for test case
    url = 'http://127.0.0.1:80'
    # -----------------------------------------------------------------------------
    testcase = 'testcase1'
    testid = requests.post('{0}/testcases/{1}/select'.format(url,testcase)).json()['testid']
    # ---------------
    # Set testing scenario
    scenario = {'time_period':'test_day', 'electricity_price':'dynamic'}
    # Set control step
    step = 300
    # -----------------------------------------------------------------------------
    # GET TEST INFORMATION
    # -----------------------------------------------------------------------------
    # Get test case name
    name = requests.get('{0}/name/{1}'.format(url, testid)).json()
    # Get inputs available
    inputs = requests.get('{0}/inputs/{1}'.format(url, testid)).json()
    # Get measurements available
    measurements = requests.get('{0}/measurements/{1}'.format(url, testid)).json()
    # -----------------------------------------------------------------------------
    # RUN TEST CASE
    # -----------------------------------------------------------------------------
    # Set control step
    requests.put('{0}/step/{1}'.format(url, testid), data={'step':step})
    # Set test case scenario
    y = requests.put('{0}/scenario/{1}'.format(url, testid), data=scenario).json()['time_period']
    # Record test start time
    start_time = y['time']
    # Simulation Loop
    while y:
        # Compute control signal
        u = pid.compute_control(y)
        # Advance simulation with control signal
        y = requests.post('{0}/advance/{1}'.format(url, testid), data=u).json()
    # -----------------------------------------------------------------------------
    # GET RESULTS
    # -----------------------------------------------------------------------------
    # Get KPIs
    kpi = requests.get('{0}/kpi/{1}'.format(url, testid)).json()
    # Get zone temperature over test period
    args = {'point_name':'TRooAir_y', 'start_time':start_time, 'final_time':np.inf}
    res = requests.put('{0}/results/{1}'.format(url, testid), data=args).json()
    # -----------------------------------------------------------------------------
    # PRINT AND VIEW RESULTS
    # -----------------------------------------------------------------------------
    print('\nKPI RESULTS \n-----------')
    for key in kpi.keys():
        if key == 'tdis_tot':
            unit = 'Kh'
        if key == 'idis_tot':
            unit = 'ppmh'
        elif key == 'ener_tot':
            unit = 'kWh'
        elif key == 'cost_tot':
            unit = 'euro or $'
        elif key == 'emis_tot':
            unit = 'kg CO2'
        elif key == 'time_rat':
            unit = ''
        print('{0}: {1} {2}'.format(key, kpi[key], unit))
    # Plot
    if plot:
        from matplotlib import pyplot as plt
        plt.figure(1)
        plt.title('Zone Temperature')
        plt.plot(res['time'], np.array(res['TRooAir_y'])-273.15)
        plt.plot(res['time'], 20*np.ones(len(res['time'])), '--')
        plt.plot(res['time'], 23*np.ones(len(res['time'])), '--')
        plt.ylabel('Temperature [C]')
        plt.xlabel('Time [hr]')
        plt.show()

    requests.put('{0}/stop/{1}'.format(url, testid))

    return kpi

if __name__ == "__main__":
    kpi = run()
