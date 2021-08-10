import xml.dom.minidom
from xml.dom import Node

from simple_salesforce.exceptions import SalesforceAuthenticationFailed
from simple_salesforce.util import getUniqueElementValueFromXmlString


def convert_lead(
    session,
    session_id,
    lead_id,
    sf_instance,
    account_id=None,
    lead_status="Closed Won",
    sandbox=False,
    proxies=None,
    sf_version="38.0",
):
    soap_url = "https://{sf_instance}/services/Soap/u/{sf_version}"
    domain = "test" if sandbox else "login"
    soap_url = soap_url.format(
        domain=domain, sf_version=sf_version, sf_instance=sf_instance
    )

    account_id_block = ""
    if account_id:
        account_id_block = "<urn:accountId>{account_id}</urn:accountId>".format(account_id=account_id)

    login_soap_request_body = """
    <soapenv:Envelope
                xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
                xmlns:urn="urn:partner.soap.sforce.com">
      <soapenv:Header>
         <urn:SessionHeader>
            <urn:sessionId>{session_id}</urn:sessionId>
         </urn:SessionHeader>
      </soapenv:Header>
      <soapenv:Body>
         <urn:convertLead> 
            <urn:leadConverts> <!-- Zero or more repetitions -->
               <urn:convertedStatus>{lead_status}</urn:convertedStatus>
               <urn:leadId>{lead_id}</urn:leadId>
               {account_id_block}
               <urn:convertedStatus>{lead_status}</urn:convertedStatus>
               <urn:sendNotificationEmail>true</urn:sendNotificationEmail>
               <urn:doNotCreateOpportunity>true</urn:doNotCreateOpportunity>
            </urn:leadConverts>
         </urn:convertLead>
      </soapenv:Body>
    </soapenv:Envelope>
    """.format(
        lead_id=lead_id,
        account_id_block=account_id_block,
        session_id=session_id,
        lead_status=lead_status,
    )
    login_soap_request_headers = {
        "content-type": "text/xml",
        "charset": "UTF-8",
        "SOAPAction": "convertLead",
    }
    response = session.post(
        soap_url,
        login_soap_request_body,
        headers=login_soap_request_headers,
        proxies=proxies,
    )
    if response.status_code != 200:
        except_code = getUniqueElementValueFromXmlString(
            response.content, "sf:exceptionCode"
        )
        except_msg = getUniqueElementValueFromXmlString(
            response.content, "sf:exceptionMessage"
        )
        raise SalesforceAuthenticationFailed(except_code, except_msg)
    else:
        response_xml = xml.dom.minidom.parseString(response.content)
        success = get_xml_value_by_path(response_xml, ('soapenv:Envelope', 'soapenv:Body', 'convertLeadResponse',
                                                       'result', 'success'))
        if success == "true":
            contact_id = get_xml_value_by_path(response_xml, ('soapenv:Envelope', 'soapenv:Body', 'convertLeadResponse',
                                                              'result', 'contactId'))
            return True, contact_id
        else:
            status_code = get_xml_value_by_path(response_xml, ('soapenv:Envelope', 'soapenv:Body',
                                                               'convertLeadResponse', 'result', 'errors', 'statusCode'))
            return False, status_code


def get_xml_value_by_path(xml_document, path):
    element = xml_document
    for step in path:
        element = get_first_child_of_xml_element_by_tag_name(element, step)
        if element is None:
            return element
    return element.firstChild.data if element.hasChildNodes() else None


def get_first_child_of_xml_element_by_tag_name(xml_element, tag_name):
    child_elements = [c for c in xml_element.childNodes if c.nodeType == Node.ELEMENT_NODE and c.tagName == tag_name]
    return child_elements[0] if child_elements else None


def get_xml_value_by_path_et(xml_doc, path):
    namespaces = {'soapenv': 'http://schemas.xmlsoap.org/soap/envelope/',
                  'default': 'urn:partner.soap.sforce.com'}
    element = xml_doc
    for step in path:
        elements = element.findall(step, namespaces=namespaces)
        if not elements:
            return None
        element = elements[0]
    return element.text


if __name__ == "__main__":
    a = """<?xml version="1.0" encoding="UTF-8"?>
    <soapenv:Envelope
            xmlns:soapenv="http://schemas.xmlsoap.org/soap/envelope/"
            xmlns="urn:partner.soap.sforce.com"
            xmlns:xsi="http://www.w3.org/2001/XMLSchema-instance"
            xmlns:sf="urn:sobject.partner.soap.sforce.com">
            <soapenv:Header>
                    <LimitInfoHeader>
                            <limitInfo>
                                    <current>68004</current>
                                    <limit>5000000</limit>
                                    <type>API REQUESTS</type>
                            </limitInfo>
                    </LimitInfoHeader>
            </soapenv:Header>
            <soapenv:Body>
                    <convertLeadResponse>
                            <result>
                                    <accountId xsi:nil="true"/>
                                    <contactId xsi:nil="true"/>
                                    <errors xsi:type="DuplicateError">
                                            <message>You&apos;re creating a duplicate record. We recommend you use an existing record instead.</message>
                                            <statusCode>DUPLICATES_DETECTED</statusCode>
                                            <duplicateResult>
                                                    <allowSave>true</allowSave>
                                                    <duplicateRule>Custom_Contact_Duplicate_Rule</duplicateRule>
                                                    <duplicateRuleEntityType>Contact</duplicateRuleEntityType>
                                                    <errorMessage>You&apos;re creating a duplicate record. We recommend you use an existing record instead.</errorMessage>
                                                    <matchResults>
                                                            <entityType>Contact</entityType>
                                                            <matchEngine>ExactMatchEngine</matchEngine>
                                                            <matchRecords>
                                                                    <fieldDiffs>
                                                                            <difference>SAME</difference>
                                                                            <name>Email</name>
                                                                    </fieldDiffs>
                                                                    <matchConfidence>100.0</matchConfidence>
                                                                    <record xsi:type="sf:sObject">
                                                                            <sf:type>Contact</sf:type>
                                                                            <sf:Id>0034C00000UQ6jIQAT</sf:Id>
                                                                            <sf:Name>Test Three</sf:Name>
                                                                            <sf:Email>zenbusinesstest+sftest+6b02d720@gmail.com</sf:Email>
                                                                            <sf:OwnerId>00546000000zAiIAAU</sf:OwnerId>
                                                                            <sf:LastModifiedDate>2021-08-05T21:51:05.000Z</sf:LastModifiedDate>
                                                                            <sf:Id>0034C00000UQ6jIQAT</sf:Id>
                                                                    </record>
                                                            </matchRecords>
                                                            <rule>Contact_Email</rule>
                                                            <size>1</size>
                                                            <success>true</success>
                                                    </matchResults>
                                            </duplicateResult>
                                    </errors>
                                    <leadId>00Q4C00000AhuQzUAJ</leadId>
                                    <opportunityId xsi:nil="true"/>
                                    <success>false</success>
                            </result>
                    </convertLeadResponse>
            </soapenv:Body>
    </soapenv:Envelope>"""
    from xml.etree import ElementTree as ET
    bb = ET.fromstring(a)
    print(get_xml_value_by_path_et(bb, ('soapenv:Body', 'default:convertLeadResponse', 'default:result',
                                        'default:success')))
    print(get_xml_value_by_path_et(bb, ('soapenv:Body', 'default:convertLeadResponse', 'default:result',
                                        'default:contactId')))
    print(get_xml_value_by_path_et(bb, ('soapenv:Body', 'default:convertLeadResponse', 'default:result', 'default:errors',
                                        'default:statusCode')))

    b = xml.dom.minidom.parseString(a)
    print(get_xml_value_by_path(b, ('soapenv:Envelope', 'soapenv:Body', 'convertLeadResponse', 'result', 'success')))
    print(get_xml_value_by_path(b, ('soapenv:Envelope', 'soapenv:Body', 'convertLeadResponse', 'result', 'contactId')))
    print(get_xml_value_by_path(b, ('soapenv:Envelope', 'soapenv:Body', 'convertLeadResponse', 'result', 'errors', 'statusCode')))

    # SALESFORCE_INSTANCE = {
    #     "username": "EMAIL@EXAMPLE.COM",
    #     "password": "EXAMPLEPASSWORD",
    #     "security_token": "SECURITY_TOKEN",
    #     "domain": "Test",
    # }
    # sf = Salesforce(**SALESFORCE_INSTANCE)
    # resp = convert_lead(
    #     sf.session,
    #     sf.session_id,
    #     lead_status="Qualified",
    #     sandbox=sf.sandbox,
    #     proxies=sf.proxies,
    #     sf_version=sf.sf_version,
    #     sf_instance=sf.sf_instance,
    #     lead_id="00Qg000000Ac6fZEAR",
    #     account_id="001g000001jOrDfAAK",
    # )
