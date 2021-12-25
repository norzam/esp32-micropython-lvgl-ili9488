class Trigger:
    
    def __init__(self):

        self.name       = ""
        self.description= ""

        self.bhour      = 0
        self.bminute    = 0
        self.bsecond    = 0

        self.ebhour     = 0
        self.eminute    = 0
        self.esecond    = 0

        self.hourdur    = 0
        self.minutedur  = 0
        self.seconddur  = 0

        self.dayOfWeek= [True, True, True, True, True, True, True, True]
    
        self.usingCalendar  = False
    
        self.usingFlowSensor= False
        self.allowFlowSensorOveride = False
        self.FlowSensorMin  = 5
        self.FlowSensorMax  = 100

        self.isTriggered    = False
        self.isArmed        = False
        self.isRansensor    = False
        self.isUsingMETAPI  = False
       


