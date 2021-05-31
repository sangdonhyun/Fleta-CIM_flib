from __future__ import print_function
import sys
# vSphere specific modules
from pyVim.connect import SmartConnect
from pyVmomi import vim

def connect_vcenter(vcenter_server):
    """
    Create a vCenter service instance.
    :param vcenter_server: Fully qualified name or IP of the vCenter server to connect to.
    :return: service_instance  # The vCenter service instance object.
    """
    try:
        # Define the vCenter service instance to connect to.
        vcenter_service_instance = SmartConnect(host=vcenter_server,
                                        user=sa_username,
                                        pwd=sa_password,
                                        port=int(443),
                                        sslContext=context)

        return service_instance

class GetSomeAwesomeVmPerformanceStats(object):
    def __init__(self, vcenter, vcenter_service_instance, query_range, time_interval, formatted_params, hr_params):
        """
        Initialize input parameters and build some basic objects to be used throughout the class.
        :param vcenter: The vCenter server that the vcenter_service_instance is built against.
        :param vcenter_service_instance: The vCenter service instance object.
        :param query_range: The range, in minutes, to find performance statistics for.
        :param time_interval: The interval, in seconds, to find performance stats for.
        :param formatted_params: The parameters to search on, formatted for the query.
        :param hr_params: The human-readable parameters that will be returned for each vm.
        """
        # Assign input parameters.
        self.vcenter = vcenter
        self.vcenter_service_instance = vcenter_service_instance
        self.query_range = query_range
        self.time_interval = time_interval
        self.formatted_params = formatted_params
        self.hr_params = hr_params

        self.content = self.vcenter_service_instance.RetrieveContent()  # Content of service instance.
        self.vc_time = self.vcenter_service_instance.CurrentTime()  # Current time on the vCenter
        self.vm_stats = []  # List of VM statistics information, updated by multiple methods.

        # Get all the performance counters, add to dictionary.
        self.perf_dict = {}
        perf_list = self.content.perfManager.perfCounter
        for counter in perf_list:
            counter_full = "{}.{}.{}".format(counter.groupInfo.key, counter.nameInfo.key, counter.rollupType)
            self.perf_dict[counter_full] = counter.key

        # get the performance manager, start time, and end time
        self.perf_manager = self.content.perfManager  # Perf manager content object, used to build query.
        self.start_time = self.vc_time - timedelta(minutes=(self.query_range + 1))  # Start time for query range.
        self.end_time = self.vc_time - timedelta(minutes=1)  # End time for query range.

    def build_query(self, counter_id, vm):  # pass a list here
        """
        get the vm's data for the given parameter
        :param counter_id: the the key of the parameter to search on
        :param vm: the vm object to query
        :return: None
        """
        metric_id = vim.PerformanceManager.MetricId(counterId=counter_id, instance="")
        query = vim.PerformanceManager.QuerySpec(intervalId=self.time_interval, entity=vm,
                                                 metricId=[metric_id], startTime=self.start_time,
                                                 endTime=self.end_time)
        perf_results = self.perf_manager.QueryPerf(querySpec=[query])
        print('perf_results size:', sys.getsizeof(perf_results))
        print('perf_results:', perf_results)

        do_something_with_perf_results(perf_results)