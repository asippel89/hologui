#/usr/bin/python

#clienttest.py
try:
    import build
    import example_client as ec
except ImportError as e:
    print "Error, connection client not loaded in python path. TCP connection will not work."
    print e
    pass

class Client:
    
    def __init__(self, report_data_method, host, port):
        
        self.report_data = report_data_method

        CSD_raw = build.TCSDavg()
        connection = build.CSDConnection(host, port)
        
        should_quit = False
        if connection.get_error():
            print "Error sucka: ", connection.get_error()
            should_quit = True

        frame_num = 0

        while not should_quit:
            connection.csd_pull(CSD_raw);
            if connection.get_error():
                print "Error sucka, couldn't read: ", connection.get_error()
                should_quit = True
                break;

            my_csd = ec.CSDCarrier(CSD_raw, frame_num)
            self.report_data(my_csd)
            frame_num += 1
            print "CSD Received"
            print 'num_coadded:', my_csd.get_num_coadded()
            print 'type(num_coadded):', type(my_csd.get_num_coadded())

if __name__ == "__main__":
    def report_data_method(thing):
        print thing

    client = Client(report_data_method, 'localhost', '12345')
