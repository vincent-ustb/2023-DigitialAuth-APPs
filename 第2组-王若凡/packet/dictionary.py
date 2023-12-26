pac_type = {'c_a': '0001', 'a_c': '0010', 'c_t': '0011', 't_c': '0100', 'c_s': '0101', 's_c': '0110'}

sign = {'none': '0000', 'user': '0001', 'business': '0010', 'rider': '0011'}

state = {'none': '0000', 'success': '0001', 'client_error': '0010', 'server_error': '0011'}

ack = {'NO': '00', 'YES': '01'}

code_type = {'ASCII': '0001', 'GBK': '0010', 'Unicode': '0011', 'utf-8': '0100'}

# 因为pac_type不同对应的control_type值有重复，因此将每个pac_type对应的control_type分开
# ticket1为票据许可票据 ticket2为服务许可票据
# type分别与pac_type与sign结合的顺序一一对应
# 文档中server发给不同client好像忘了写
# 后续删除0b且全打''
control_type1 = {'get_ticket1': '0001', 'request_enroll': '0010', 'modify_pwd': '0011', 'unknown1': '0100'}

control_type2 = {'return_ticket1': '0001', 'ACK': '0010', 'unknown1': '0011', 'unknown2': '0100'}

control_type3 = {'request_ticket2': '0001', 'unknown1': '0010', 'unknown2': '0011'}

control_type4 = {'return_ticket2': '0001', 'unknown1': '0010', 'unknown2': '0011'}

control_type5 = {'request_serve': '0001', 'add_cart': '0010', 'recharge': '0011',
                 'product_details': '0100', 'submit': '0101', 'order_details': '0110',
                 'modify': '0111', 'get_menu': '1000', 'ACK': '1001', 'unknown1': '1010',
                 'unknown2': '1011', 'unknown3': '1100'}

control_type6 = {'product_details': '0001', 'order_details': '0010', 'work': '0011', 'get_off': '0100',
                 'modify_product': '0101', 'new_product': '0110', 'delete_product': '0111', 'search_order': '1000',
                 'finish_order': '1001', 'modify': '1010', 'unknown1': '1011', 'unknown2': '1100', 'unknown3': '1101',
                 'unknown4': '1110', 'unknown5': '1111'}

control_type7 = {'modify': '0001', 'work': '0010', 'get_off': '0100', 'salary': '0101', 'search_order': '0110',
                 'finish_order': '0111', 'unknown1': '1000', 'unknown2': '1001', 'unknown3': '1010'}

# 分别是s-c1 ，s-c2， s-c3
control_type8 = {'respond_request_serve': '0001', 'respond_add_cart': '0010', 'respond_recharge': '0011',
                 'respond_product_details': '0100', 'respond_submit': '0101', 'respond_order_details': '0110',
                 'respond_modify': '0111', 'respond_get_menu': '1000', 'ACK': '1001', 'unknown1': '1010',
                 'unknown2': '1011', 'unknown3': '1100'}

control_type9 = {'respond_product_details': '0001', 'respond_order_details': '0010', 'respond_work': '0011',
                 'respond_get_off': '0100', 'respond_modify_product': '0101', 'respond_new_product': '0110',
                 'respond_delete_product': '0111', 'respond_search_order': '1000', 'respond_finish_order': '1001',
                 'respond_modify': '1010', 'unknown1': '1011', 'unknown2': '1100', 'unknown3': '1101',
                 'unknown4': '1110', 'unknown5': '1111'}

control_type10 = {'respond_modify': '0001', 'respond_work': '0010', 'respond_get_off': '0100', 'respond_salary': '0101',
                  'respond_search_order': '0110','respond_finish_order': '0111', 'unknown1': '1000',
                  'unknown2': '1001', 'unknown3': '1010'}
