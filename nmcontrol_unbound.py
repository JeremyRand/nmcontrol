#!/usr/bin/env python2

import nmcontrol
import json

blockchain_ttl = 60

def init(id, cfg):
   log_info("pythonmod: init called, module id is %d port: %d script: %s" % (id, cfg.port, cfg.python_script))
   return True

def deinit(id):
   log_info("pythonmod: deinit called, module id is %d" % id)
   return True

def inform_super(id, qstate, superqstate, qdata):
   return True

def operate(id, event, qstate, qdata):
    if (event == MODULE_EVENT_NEW) or (event == MODULE_EVENT_PASS):
        if (qstate.qinfo.qname_str.endswith(".bit.")): #query name ends with localdomain
            #create instance of DNS message (packet) with given parameters
            #msg = DNSMessage(qstate.qinfo.qname_str, RR_TYPE_A, RR_CLASS_IN, PKT_QR | PKT_RA | PKT_AA)
            msg = DNSMessage(qstate.qinfo.qname_str, RR_TYPE_A, RR_CLASS_IN, PKT_QR | PKT_AA)
            #append RR
            
            ### TODO: detect nonexistent .bit domain and return NXDOMAIN
            
            # Process NS
            addrs = json.loads(nmcontrol.app['plugins']['dns'].getNs(qstate.qinfo.qname_str[:-1]))
            for addr in addrs:
                msg.authority.append("%s %d IN NS %s" % (qstate.qinfo.qname_str, blockchain_ttl, str(addr)) )
            
            # Process A
            if (qstate.qinfo.qtype == RR_TYPE_A) or (qstate.qinfo.qtype == RR_TYPE_ANY):
                addrs = json.loads(nmcontrol.app['plugins']['dns'].getIp4(qstate.qinfo.qname_str[:-1]))
                
                for addr in addrs:
                    msg.answer.append("%s %d IN A %s" % (qstate.qinfo.qname_str, blockchain_ttl, str(addr)) )
            
            # Process AAAA
            if (qstate.qinfo.qtype == RR_TYPE_AAAA) or (qstate.qinfo.qtype == RR_TYPE_ANY):
                addrs = json.loads(nmcontrol.app['plugins']['dns'].getIp6(qstate.qinfo.qname_str[:-1]))
                
                for addr in addrs:
                    msg.answer.append("%s %d IN AAAA %s" % (qstate.qinfo.qname_str, blockchain_ttl, str(addr)) )
            
            #set qstate.return_msg 
            if not msg.set_return_msg(qstate):
                qstate.ext_state[id] = MODULE_ERROR 
                return True

            # Namecoin blockchain results are secure by default
            qstate.return_msg.rep.security = 2

            qstate.return_rcode = RCODE_NOERROR
            qstate.ext_state[id] = MODULE_FINISHED 
            return True
        else:
            #pass the query to validator
            qstate.ext_state[id] = MODULE_WAIT_MODULE 
            return True

    if event == MODULE_EVENT_MODDONE:
        log_info("pythonmod: iterator module done")
        qstate.ext_state[id] = MODULE_FINISHED 
        return True
      
    log_err("pythonmod: bad event")
    qstate.ext_state[id] = MODULE_ERROR
    return True

nmcontrol.init()

log_info("pythonmod: script loaded.")