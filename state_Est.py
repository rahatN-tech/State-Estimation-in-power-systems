import pandapower as pp
import numpy as np
import pandas as pd
import pandapower.estimation as est
import pandapower.networks as nw

# ============define network==================================================
net = nw.case33bw()
pp.create_gen(net, 21, p_mw =0.2,q_mvar =0.05, type ="PV", in_service =True)
pp.create_gen(net, 31, p_mw =0.5,q_mvar =0.02, type ="PV", in_service =True)
pp.create_gen(net, 7, p_mw =0.2,q_mvar =0.05, type ="PV", in_service =True)
pp.create_gen(net, 15, p_mw =0.1,q_mvar =0.01, type ="PV", in_service =True)


# ==========================measurement data fr 1 year==========================================================
data= pd.read_csv('./orig_z_1_yr.csv').drop("Unnamed: 0", axis="columns")


# ============================================================================================================

column_a = []
column_vm = []

for n in range(len(net.bus.index)):
    column_a.append('a' + str(n))
    column_vm.append('v' + str(n))
    se_a = pd.DataFrame(columns=column_a)
    se_v = pd.DataFrame(columns=column_vm)


# time samples in one yr data = 35135 (at 15-mins interval)
timestamps = list(range(35135)) 
for t in timestamps:
    for n in range(len(net.bus.index)):
      
        column_v = 'v' + str(n)
        column_p = 'p' + str(n)
        column_q = 'q' + str(n)
        column_pl = 'pl' + str(n)
        column_ql = 'ql' + str(n)
        bus_no = n
        
        measuremnt_v_pu = 1
        
        measuremnt_p_mw = (data._get_value(t, column_p))
        
        measuremnt_q_mvar = (data._get_value(t, column_q))
        
        pp.create_measurement(
            net, 'v', 'bus', measuremnt_v_pu, .01, bus_no)
        pp.create_measurement(
            net, 'p', 'bus',  measuremnt_p_mw, 0.01, bus_no)
        pp.create_measurement(
            net, 'q', 'bus', measuremnt_q_mvar, 0.01, bus_no)
        # pp.create_measurement(
        # net, 'p', 'line',  measuremnt_p_mw, 0.00001, bus_no, side='from')
        # pp.create_measurement(
        # net, 'q', 'line',  measuremnt_p_mw, 0.00001, bus_no, side='from')

    for l in range(len(net.line.index)):
        # print('lines')
        column_pl = 'pl' + str(l)
        column_ql = 'ql' + str(l)

        measuremnt_pl_mw = (data._get_value(t, column_pl))
        # print(measuremnt_pl_mw)
        measuremnt_ql_mvar = (data._get_value(t, column_ql))

        pp.create_measurement(
            net, 'q', 'line', measuremnt_ql_mvar, 0.02, l, side='from')
        pp.create_measurement(
            net, 'p', 'line', measuremnt_pl_mw, 0.01, l, side='from')

    success = est.estimate(net, init="flat")

    est.estimate(net)
    print('success')
    print(pp.diagnostic(net, report_style='detailed') )
    
    state_values = [net.res_bus_est['vm_pu'], net.res_bus_est['va_degree']]
    se_v.loc[t] = np.array(net.res_bus_est['vm_pu'])
    se_a.loc[t] = np.array(net.res_bus_est['va_degree'])
    #
se_v.to_csv('./v_est_1_yr.csv')
se_a.to_csv('./theta_est_1_yr.csv')
# print(se_v)

x_est = pd.concat([se_a,se_v],axis = 1)

# print(se_a)
