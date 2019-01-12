import random

class Interest:
    total_len = 0
    def __init__(self, pos, content_name, pathlen = 0 ):
        self.pos = pos
        self.content_name = content_name
        self.len = pathlen
        self.random = random.randint(0, 100)

    def add(self):
        self.len += 1
        Interest.total_len += 1

class Notify:
    def __init__(self, dest_pos, new_pos, content_name, tm=64):
        self.dest_pos = dest_pos
        self.new_pos = new_pos
        self.content_name = content_name
        self.tm = tm

class Data:
    total_len = 0
    def __init__(self,name,data,pathlen = 0):
        self.name = name
        self.data = data
        self.len = pathlen
    def add(self):
        self.len += 1
        Data.total_len += 1

class LC:
    def __init__(self, new_pos, content_name):
        self.new_pos = new_pos
        self.content_name = content_name

class Node:
    def __init__(self, routename):
        self.PIT = {}
        self.RT = {}  # name : pos
        self.FIB = {}
        self.CS = {}
        self.name = routename

    def set_FIB(self, name, nxt):
        self.FIB[name] = nxt

    def find_FIB(self, name):
        #print(self.name,'findFIB:',name)
        if name in self.FIB:
            return self.FIB[name]
        group_name = name.split('/')
        for i in range(1, len(group_name)-1):
            tmp = '/'.join(group_name[:-i])
            if tmp in self.FIB:
                #print('find->',tmp)
                return self.FIB[tmp]
        return None

    def get_route_from_PIT(self,name):
        ans = []
        if name not in self.PIT:
            return []
        for i in self.PIT[name]:
            ans.append(self.PIT[name][i])
        return ans

    def add_PIT(self, name, rd, route):
        if route:
            if name not in self.PIT:
                self.PIT[name] = {}
            self.PIT[name][rd] = route

    def find_PIT(self,name,rd):
        if name not in self.PIT:
            return None
        else:
            if rd in self.PIT[name]:
                return self.PIT[name][rd]
            return -1

    def update_RT(self, name, pos):
        self.RT[name] = pos

    def find_CS(self, interest):
        if interest.content_name in self.CS:
            return self.CS[interest.content_name]
        return None

    def update_CS(self, content_name, data):
        self.CS[content_name] = data

    def handle_lc(self, lc):
        self.RT[lc.content_name] = lc.new_pos
        #print('++++++', self.name, self.RT)
        #print('PIT=',self.PIT)
        if lc.content_name in self.PIT:
            #l = self.PIT[lc.content_name]
            l = self.get_route_from_PIT(lc.content_name)
            self.PIT.pop(lc.content_name)
            #self.PIT[lc.content_name] = []
            for i in l:
                i.handle_lc(lc)

    def handle_NF(self,notify):
        #print(self.name,':handle_NF',notify.dest_pos,',',notify.new_pos,',',notify.content_name)
        if notify.dest_pos == self.name:
            #self.RT[notify.content_name] = notify.new_pos
            lc = LC(notify.new_pos,notify.content_name)
            self.handle_lc(lc)
            return
        nxt = self.find_FIB(notify.dest_pos)
        if nxt:
            nxt.handle_NF(notify)
            return

    def handle_int(self, interest, src):
        interest.add()
        print('int(',interest.content_name,',',interest.pos,')')
        if src:
            print(src.name,'->',self.name)
        else:
            print(self.name)
        cs_tmp = self.find_CS(interest)
        if cs_tmp:
            src.handle_data(cs_tmp)
            return
        #print('-||||-',self.RT)
        if interest.content_name in self.RT and interest.pos != self.RT[interest.content_name]:
            self.add_PIT(interest.content_name,interest.random,src) #添加PIT是为了后面处理流程LC包需要用到
            lc = LC(self.RT[interest.content_name], interest.content_name)
            self.handle_lc(lc)
            return
        rt = self.find_PIT(interest.content_name,interest.random)
        if rt:                  #说明PIT表中有该内容名的项，不必转发，记录即可
            if rt == -1:        #说明没用random值这项，此时加入
                self.add_PIT(interest.content_name,interest.random,src)
            return
        nxt = self.find_FIB(interest.pos)
        if nxt :
            if src:
                self.add_PIT(interest.content_name,interest.random,src)
                #self.PIT[interest.content_name] = []
                #self.PIT[interest.content_name].append(src)
            nxt.handle_int(interest, self)

    def handle_data(self, data):
        data.add()
        if data.name in self.PIT:
            #l = self.PIT[data.name]
            l = self.get_route_from_PIT(data.name)
            self.PIT.pop(data.name)
            for i in l:
                #print('pass',self.name,'->',i.name)
                i.handle_data(data)

    def connect(self, route):
        self.set_FIB(route.name,route)
        route.set_FIB(self.name,self)

class Product(Node):
    rd = 0

    def __init__(self, name):
        super(Product, self).__init__(name)
        self.last_cn = None
        self.last_name = None
        self.content_name = None

    def handle_int(self, interest, src):
        print('from ', src.name, ' arraived ', self.name, 'int len = ', interest.len)
        interest.add()
        Product.rd += 1
        data = Data(interest.content_name,"hahah"+ str(Product.rd))
        src.handle_data(data)

    def change_pos(self,new_name,route):
        nf = Notify(self.last_cn.name,  new_name, self.content_name)
        route.handle_NF(nf)

    def connect(self, route, souce_name):
        if self.last_cn:
            print('last cn',self.last_cn.name)
            self.last_cn.FIB.pop(self.last_name)
            self.change_pos(souce_name,route)
        route.set_FIB(souce_name, self)
        self.last_cn = route
        self.last_name = souce_name
        if self.content_name is None:
            self.content_name = souce_name

    def handle_data(self, data):
        pass

class Costomer(Node):
    def __init__(self, name):
        super(Costomer, self).__init__(name)

    def gen_int(self,content_name):
        pos = content_name
        if content_name in self.RT:
            pos = self.RT[content_name]
        it = Interest(pos,content_name)
        self.handle_int(it,None)

    def handle_lc(self, lc):
        it = Interest(lc.new_pos, lc.content_name)
        self.RT[lc.content_name] = lc.new_pos
        self.handle_int(it, None)

    def handle_data(self, data):
        data.add()
        print('customer get ',data.name,'=',data.data,',data_len=',data.len)
