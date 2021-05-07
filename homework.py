#%%
import re
from copy import deepcopy
from collections import deque
import time

class Predicate:
    def __init__(self,predname,arg,neg,val,sentence_id,predicate_id) -> None:
        self.neg=neg
        self.name=predname
        self.args=arg
        self.val=self.self_val()
        self.sentence_id=sentence_id
        self.predicate_id=predicate_id
        self.literal=self.is_literal()
    
    def replace_arg(self,d:dict):
        #print('Before Replacement in', self.name,self.args)
        self.args=[d.get(n,n) for n in self.args]
        self.val=self.self_val()
        self.literal=self.is_literal()
        #print('After Replacement in', self.name,self.args)
        #self.args=[d[x] if x in d else x for x in self.args]

    def change_pred_id(self,new_id:int):
        self.predicate_id=new_id

    def is_literal(self):
        for i in self.args:
            if i[0].islower(): 
                self.literal=False
                return False
        self.literal=True
        return True

    def self_val(self):
        return ('~' if self.neg else '')+self.name+'('+','.join(self.args)+')'

    def __str__(self) -> str:
        return self.self_val()

    def __eq__(self, o: object) -> bool:
        if self.name!=o.name: return False
        if not isinstance(o,type(self)): return False
        if len(self.args)!=len(o.args): return False
        if self.literal and o.literal:
            for my,ot in zip(self.args,o.args):
                if my!=ot: return False
        for my,ot in zip(self.args,o.args):
            if my[0].isupper():
                if ot[0].isupper(): 
                    if my!=ot: return False
            elif ot[0].isupper():
                if my[0].isupper():
                    if my!=ot: return False
        return True
    
class Sentence:
    def __init__(self,prednames:list,id:int) -> None:
        self.predicates=prednames
        self.id=id
        self.constant=self.is_constant()
        self.val=self.self_val()
    
    def self_val(self):
        self.val='|'.join([x.val for x in self.predicates])
        return '|'.join([x.val for x in self.predicates])

    def replace_pred_arguments(self,d:dict):
        for x in self.predicates: x.replace_arg(d)
        self.val=self.self_val()
        self.constant=self.is_constant()

    def remove_predicate(self,pred:Predicate):
        self.predicates=[x for x in self.predicates if x.predicate_id!=pred.predicate_id]
    
    def refresh_predicate_id(self):
        for i,x in enumerate(self.predicates): x.change_pred_id(i)
    
    def length(self): return len(self.predicates)

    def negation_of(self, o:object)->bool:
        if type(self)!=type(o): return False
        self.self_val()
        o.self_val()
        for ac1,ac2 in zip(self.predicates[0].args,o.predicates[0].args):
            #print('In Unify Outer\t\t\t',ac1,ac2)
            a1,a2=ac1[0],ac2[0]
            if a1.isupper() and a2.isupper():
                #print('In Unify\t\t\t',ac1,ac2)
                if ac1!=ac2: 
                    #print('here1')
                    return False
            #elif a1.islower() and a2.islower():
                #return False,{},{}
                #if a2 in cl1.args: return False,{},{}
                #unifier_rev[ac1]=ac2
            elif a2.islower():
                if ac2 in self.predicates[0].args: 
                    return False
                #unifier_rev[ac2]=ac1
            elif a1.islower():
                if ac1 in o.predicates[0].args: 
                    #print('here3')
                    return False
                #unifier[ac1]=ac2
        return len(self)==len(o) and len(self)==1 and self.predicates[0].neg!=o.predicates[0].neg and self.predicates[0].name==o.predicates[0].name

    def is_constant(self):
        d=all([x.is_literal() for x in self.predicates])
        self.constant=d
        return d
    
    def is_empty(self):
        self.self_val()
        return self.val==''

    def __eq__(self, o: object) -> bool:
        self.self_val()
        o.self_val()
        return self.val==o.val and type(self)==type(o)

    def __len__(self) -> int:
        return len(self.predicates)

    def __str__(self) -> str:
        return self.self_val()

class KB:
    def __init__(self,sentences:list=[]) -> None:
        self.sentences=sentences
    
    def tell(self,sentence:Sentence):
        self.sentences.append(sentence)
    
    def __str__(self) -> str:
        return '\n'.join([str(x.id)+'\t'+str(x) for x in self.sentences])

    def print_all(self):
        for ix,s in enumerate(self.sentences):
            print(ix,s,sep='\t')
    
    def __len__(self) -> int:
        return len(self.sentences)

    def __eq__(self, o: object) -> bool:
        if type(o)!=type(self): return False
        if len(self)!=len(o): return False
        for s1,s2 in zip(self.sentences,o.sentences):
            if s1!=s2: return False
        return True
    
    def ask(self,sentence:Sentence):
        return

class SafeTreeNode:
    def __init__(self,val,head=False,leaf=False) -> None:
        self.val=val
        self.is_head=head
        self.is_leaf=leaf
        self.next={}

class PuppyAcademy:

    def __init__(self,ip='testcases\input_1.txt',op='output.txt') -> None:
        self.ip=ip
        f=open(self.ip,'r').read()
        self.op=op
        lines=f.split('\n')
        self.n=int(lines[0])
        self.queries=[x.replace(' ','').strip() for x in lines[1:self.n+1]]
        self.k=int(lines[self.n+1])
        self.kb=[x.replace(' ','') for x in lines[self.n+2:self.n+2+self.k]]
        self.op_precedence={'~':4,'&':3,'|':2,'=>':1}
        self.KBTree={}
        self.KBase=KB()
        self.query_stack=deque([])
        self.checked_sentences=set()
        self.used_combos={}
        self.query_stack_map={}

    def to_cnf(self,clause:str,idx:int,query_clause:bool=False)->str:
        variables=set()
        if '=>' in clause:
            lhs,rhs=clause.split('=>')[0],clause.split('=>')[1]
            if '&' in lhs and '|' not in lhs: 
                lhs = '|'.join([x[1:] if x[0]=='~' else '~'+x for x in lhs.split('&')])
                clause=lhs+'|'+rhs
            elif '|' in lhs and '&' not in lhs: 
                lh=[]
                for l in lhs.split('|'):
                    if l[0]=='~': lh.append(l[1:]+'|'+rhs)
                    else: lh.append('~'+l+'|'+rhs)
                if len(lh)>1: 
                    #print('Here***')
                    self.kb.extend(lh[1:])
                    self.k+=1
                clause=lh[0]
            else:
                if lhs[0]=='~': clause=lhs[1:]+'|'+rhs 
                else: clause='~'+lhs+'|'+rhs
        else:
            if '&' in clause:
                csplt=clause.split('&')
                if len(csplt)>1: 
                    self.kb.extend(csplt[1:])
                    self.k+=1
                clause=csplt[0]
        for v in re.findall(r'\((.*?)\)',clause):
            for s in v.split(','): 
                if s[0].islower(): variables.add(s)
        for v in list(variables): 
            if not v[0].islower(): continue
            clause=clause.replace('('+v,'('+v+str(idx))
            clause=clause.replace(','+v,','+v+str(idx))
        cl=clause.split('|')
        #print(idx)
        pred_list=[]
        sent=Sentence([],idx)
        for i,c in enumerate(cl):
            neg=False
            if c[0]=='~': 
                neg=True
            fname=c[1:c.find('(')] if neg else c[0:c.find('(')]
            if query_clause: 
                if neg: c=c[1:]
                else: c='~'+c
                neg = not neg
            new_predicate=Predicate(fname,re.findall(r'\((.*?)\)',c)[0].split(','),neg,c,idx,i)
            pred_list.append(c)
            sent.predicates.append(new_predicate)
            if fname not in self.KBTree.keys(): self.KBTree[fname]=[]
            self.KBTree[fname].append((idx,neg))
            #print(new_predicate.name,end='\t')
            if fname not in self.KBTree.keys(): self.KBTree[fname]=[]
            '''
            curr=self.KBTree[fname]
            for arg in re.findall(r'\((.*?)\)',c)[0].split(','):
                curr.next[arg]=SafeTreeNode(arg)
                curr=curr.next[arg]
            curr.next[(neg,idx)]=SafeTreeNode((neg,idx),leaf=True)
            curr=curr.next'''
        #print()
        #if sent.length()==1 and sent.constant and not query_clause: self.query_stack.append(sent)
        self.KBase.tell(sent)
            #print(c,fname,neg)
        #print(clause)
        return '|'.join(pred_list)

    def unify(self,cl1:Predicate,cl2:Predicate):
        if cl1.name==cl2.name and cl1.neg==(not cl2.neg) and cl1.args==cl2.args: return None, {},{} # Complimentary for Contradiction
        if cl1!=cl2: 
            #print('here4')
            return False,{},{}
        if cl1.neg==cl2.neg: 
            #print('here5')
            return False, {},{}
        if len(cl1.args)!=len(cl2.args): 
            #print('here6')
            return False, {},{} # unification fails here
        unifier={}
        unifier_rev={}
        for ac1,ac2 in zip(cl1.args,cl2.args):
            #print('In Unify Outer\t\t\t',ac1,ac2)
            a1,a2=ac1[0],ac2[0]
            if a1.isupper() and a2.isupper():
                #print('In Unify\t\t\t',ac1,ac2)
                if ac1!=ac2: 
                    #print('here1')
                    return False,{},{}
            #elif a1.islower() and a2.islower():
                #return False,{},{}
                #if a2 in cl1.args: return False,{},{}
                #unifier_rev[ac1]=ac2
            elif a2.islower():
                if ac2 in cl1.args: 
                    return False,{},{}
                unifier_rev[ac2]=ac1
            elif a1.islower():
                if ac1 in cl2.args: 
                    #print('here3')
                    return False,{},{}
                unifier[ac1]=ac2
        return True, unifier, unifier_rev

    def resolution(self,start_time:float,time_limit:float):
        #print('Intial query stack')
        #for xi,xd in enumerate(self.query_stack): print(xi,xd)
        while self.query_stack:
            if time.time()-start_time>=time_limit: 
                for sentence in self.KBase.sentences: # Checking for variable contradiction
                    #print(sentence,len(sent))
                    if len(sentence.predicates)==1:
                        same_f_sentences=self.KBTree[sentence.predicates[0].name]
                        for st,xt in same_f_sentences:
                            stx=self.KBase.sentences[st]
                            if sentence.negation_of(stx):
                                print('Contradiction Found case 4 ->',sentence,'\tand \t',stx)
                                return True
                print('Query Aborted')
                #print(self.KBase)
                return False
            q=self.query_stack.pop()
            self.query_stack.appendleft(q)
            if q.val=='': continue
            #if q.val=='RedNoseRaindeer(Bob)': print('Found this shit')
            #print('Current Query:',q)
            possible_unifications=[]
            for query_preds in q.predicates:
                possible_unifications.append(set([x for x in self.KBTree[query_preds.name] if x[1]==(not query_preds.neg)]))
            s=set.union(*possible_unifications)
            #print(s)
            #print('\t',q,possible_unifications,len(self.query_stack),s)
            #print('Possible sentence matches',s)
            for sent_no,neg in s:
                sent=self.KBase.sentences[sent_no]
                if q.id in self.used_combos:
                    #print(q.id,self.used_combos)
                    if sent.id in self.used_combos[q.id]: continue
                for pr in sent.predicates:
                    for query_pr in q.predicates:    
                        if pr.name==query_pr.name and query_pr.neg ==(not pr.neg):
                            #print('\t',pr.sentence_id,sent,'\t',q,query_pr.sentence_id)
                            can_unify, uni1,uni2 = self.unify(pr,query_pr)
                            #print('\t Can be unified?',can_unify,uni1,uni2)
                            if can_unify==None: 
                                if len(q.predicates)==len(sent.predicates) and q.constant and sent.constant and len(q.predicates)==1: 
                                    print('Contradiction Found case 1 ->',q,'\tand \t',sent)
                                    return True
                                if len(q.predicates)==1:
                                    #print('Special Case\t',q)
                                    sent_copy=deepcopy(sent)
                                    sent_copy.remove_predicate(pr)
                                    self.k+=1
                                    new_sentence=Sentence(sent_copy.predicates,self.k)
                                    '''
                                    if not new_sentence.constant: 
                                        self.k-=1
                                        continue
                                    '''
                                    fl=False
                                    for prds in new_sentence.predicates:
                                        for n in self.KBTree[prds.name]:
                                            if self.KBase.sentences[n[0]]==new_sentence:
                                                fl=True
                                                break
                                        if fl==True: break
                                    if fl: 
                                        self.k-=1
                                        continue
                                    self.kb.append(new_sentence.val)
                                    self.KBase.tell(new_sentence)
                                    for n in new_sentence.predicates: self.KBTree[n.name].append((self.k,n.neg))
                                    #print(new_sentence.id,new_sentence,'\t',q,q.id,'\t',sent,sent.id)
                                    #if new_sentence.length()==1 and new_sentence.constant: self.query_stack.append(new_sentence)
                                    if new_sentence.is_constant(): 
                                        #self.query_stack.append(new_sentence)
                                        if len(new_sentence.predicates)==1: 
                                            #print('adding in stack special case\t',new_sentence) 
                                            self.query_stack.append(new_sentence)
                                        #elif len(new_sentence.predicates)<=3: self.query_stack.appendleft(new_sentence)
                                        #else: self.query_stack.appendleft(new_sentence)
                                    if new_sentence.is_empty(): 
                                        print('Contradiction Found case 2 ->',q,'\tand \t',sent)
                                        return True
                                    if q.id not in self.used_combos: self.used_combos[q.id]=[]
                                    self.used_combos[q.id].append(sent.id)
                            elif can_unify:
                                sent_copy=deepcopy(sent)
                                q_copy=deepcopy(q)
                                q_copy.remove_predicate(query_pr)
                                sent_copy.remove_predicate(pr)                        
                                sent_copy.replace_pred_arguments(uni1)
                                q_copy.replace_pred_arguments(uni2)
                                self.k+=1
                                new_sentence=Sentence(sent_copy.predicates+q_copy.predicates,self.k)
                                new_sentence.refresh_predicate_id()
                                '''
                                if not new_sentence.constant: 
                                    #print('\t\t But not constant')
                                    self.k-=1
                                    continue
                            '''
                                fl=False
                                for prds in new_sentence.predicates:
                                    for n in self.KBTree[prds.name]:
                                        if self.KBase.sentences[n[0]]==new_sentence:
                                            fl=True
                                            break
                                    if fl==True: break
                                if fl: 
                                    self.k-=1
                                    continue
                                '''if len(new_sentence.predicates)==1 and not new_sentence.is_constant():
                                    for n1,n2 in self.KBTree[new_sentence.predicates[0].name]:
                                        if '''

                                #print(new_sentence.id,new_sentence,'\t',q,q.id,'\t',sent,sent.id)
                                self.kb.append(new_sentence.val)
                                self.KBase.tell(new_sentence)
                                if new_sentence.is_empty(): 
                                    print('Contradiction Found case 2 ->',q,'\tand \t',sent)
                                    return True
                                #for i in new_sentence.predicates: print(i,i.predicate_id)
                                for n in new_sentence.predicates: self.KBTree[n.name].append((self.k,n.neg))
                                #print('\t',new_sentence)
                                #if new_sentence.length()==1 and new_sentence.constant: self.query_stack.append(new_sentence)
                                if new_sentence.is_constant(): 
                                    #self.query_stack.append(new_sentence)
                                    if len(new_sentence.predicates)==1: self.query_stack.append(new_sentence)
                                    #else: self.query_stack.appendleft(new_sentence)
                                if q.id not in self.used_combos: self.used_combos[q.id]=[]
                                self.used_combos[q.id].append(sent.id)
                        elif str(sent.val)==str(q) and len(sent.predicates)==1:
                            print('Fallacy',sent,'\t',q,str(sent.val)==str(q))
                            return False
            #print(len(self.query_stack))
            for sentence in self.KBase.sentences: 
                if q.val==sentence.val and q.id!=sentence.id and q.val!='':
                    print('Duplicate/Affirmation Found for negated query', q,q.id,'\tand\t',sentence,sentence.id)
                    return False
                if q.negation_of(sentence) and q.id!=sentence.id: 
                    print('Contradiction Found case 3 ->',q,'\tand \t',sentence)
                    return True
            next_k=self.k
            
            #print(self.k)
        return False

    def print_output(self,answer_list:list): open(self.op,'w').write('\n'.join(answer_list))

    def create_query_stack(self)->None:
        self.query_stack=deque([])
        for sent in self.KBase.sentences:
            if sent.length()==1 and sent.is_constant(): 
                self.query_stack.append(sent)
            #if sent.constant: self.query_stack.append(sent)
        print('Query Stack:')
        for x in self.query_stack: print(x)
        #print('***')
    
    def answer(self):
        i=0
        while i<self.k: #* Converting to CNF
            self.kb[i]=self.to_cnf(self.kb[i],i)
            i+=1
        answer_list=[]
        KBase_copy=deepcopy(self.KBase)
        kb_copy=deepcopy(self.kb)
        KBtree_copy=deepcopy(self.KBTree)
        original_k=self.k
        #print(KBase_copy)
        for query in self.queries:
            #print('Query:\t',query)
            self.kb.append(self.to_cnf(query,i,True))
            #for id,x in enumerate(self.kb): print(id,x)
            self.create_query_stack()
            #for x in self.query_stack: print(x)
            #self.query_stack.append(self.KBase.sentences[-1])
            time_limit=10
            #t1=time.time()
            resolve=self.resolution(time.time(),time_limit)
            #print(time.time()-t1,'seconds')
            #print(query,resolve)
            #print('--------------------')
            self.KBase=deepcopy(KBase_copy)
            self.k=original_k
            self.kb=deepcopy(kb_copy)
            self.KBTree=deepcopy(KBtree_copy)
            #if resolve: self.kb.append(self.to_cnf(query,i,False))
            self.checked_sentences=set()
            self.used_combos={}
            #self.KBase.print_all()
            answer_list.append(str(resolve).upper())
        self.print_output(answer_list)

if __name__=="__main__":
    p=PuppyAcademy()
    #tx=time.time()
    p.answer()
    #print('Total Time Taken',time.time()-tx)