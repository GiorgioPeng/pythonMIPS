import os
global pc
filename = ''   #the file name
pc = 0x00400000 #the address
address = []    #store address of each instruction
pro_content = [] #the content of the file which is not manipulated
content = []    #store the content of each instruction
b_c = []        #store the machine code of each instruction
op = ''         #store the operator number
rs = ''         #store the first operator number
rt = ''         #store the second operator number
rd = ''         #store the destination operator number
shamt =''       #store the bit of move
function = ''   #store the function code
const = ''      #store the constant number of the i-type instruction
address_offset = '' #store the address_offset
dic_register = dict.fromkeys(list(range(32)),0) #record values of each registers
labels = {}     #the labels use record the address_offset of the jump operator to run the program
labels_position = {}
content_code = [] #store the new code if these are some instructions which should be divided by 2 parts

#get the content of the txt file
def get_content():
    global pc
    f = open(filename,'r')
    for i in f.readlines():
        if i.isspace(): #if there is an empty line, then skip the line
            continue
        if i.count(':') == 1 and i[-2:-1] != ':':#if the label and the sentence in the same line,divide them to two lines
            print( i[-2:-1])
            pro_content.append(i[0:i.index(':')+1])
            pro_content.append(i[i.index(':')+1:])
        else:
            pro_content.append(i)

    count = 0
    for i in range(len(pro_content)):   #store every instruction and its address
        if pro_content[i].count(':') != 1:
            pro_content[i] = pro_content[i].strip()
            content.append(pro_content[i])
            address.append(pc)
            pc = pc+4
            count += 1
        else:
            pro_content[i] = pro_content[i].strip()
            labels_position[pro_content[i][0:-1]] = count
    f.close()

#get the machine value of each register
def register(rg):
    result = ''
    if rg == '$zero':
        result = '00000'
    elif rg == '$at':
        result = '00001'
    elif rg == '$v0':
        result = '00010'
    elif rg == '$v1':
        result = '00011'
    elif rg == '$a0':
        result = '00100'
    elif rg == '$a1':
        result = '00101'
    elif rg == '$a2':
        result = '00110'
    elif rg == '$a3':
        result = '00111'
    elif rg == '$t0':
        result = '01000'
    elif rg == '$t1':
        result = '01001'
    elif rg == '$t2':
        result = '01010'
    elif rg == '$t3':
        result = '01011'
    elif rg == '$t4':
        result = '01100'
    elif rg == '$t5':
        result = '01101'
    elif rg == '$t6':
        result = '01110'
    elif rg == '$t7':
        result = '01111'
    elif rg == '$s0':
        result = '10000'
    elif rg == '$s1':
        result = '10001'
    elif rg == '$s2':
        result = '10010'
    elif rg == '$s3':
        result = '10011'
    elif rg == '$s4':
        result = '10100'
    elif rg == '$s5':
        result = '10101'
    elif rg == '$s6':
        result = '10110'
    elif rg == '$s7':
        result = '10111'
    elif rg == '$t8':
        result = '11000'
    elif rg == '$t9':
        result = '11001'
    elif rg == '$k0':
        result = '11010'
    elif rg == '$k1':
        result = '11011'
    elif rg == '$gp':
        result = '11100'
    elif rg == '$sp':
        result = '11101'
    elif rg == '$fp':
        result = '11110'
    elif rg == '$ra':
        result = '11111'
    return result

#to get the 16 bit of a decimal
def decToBin(i):
    return (bin(((1 << 16) - 1) & i)[2:]).zfill(16)

#translate the Mips instruction to the bytecode
def bytecode():
    global pc
    for i in range(len(content)):
        temp = content[i].split(' ')
        for j in range(temp.count('')):
            temp.remove('')
        if len(temp) == 0:
            pass
        elif temp[0].lower() == 'add':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            function = '100000'
            shamt = '00000'
            op = '000000'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'sub':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            function = '100010'
            shamt = '00000'
            op = '000000'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'addi':
            content_code.append((temp[0].lower())+" "+(temp[1].lower()))
            op = '001000'
            rd = register((temp[1].lower().split(','))[1])          #get the source
            rs = register((temp[1].lower().split(','))[0])          #get the destination
            const = bin(int((temp[1].lower().split(','))[2]))[2:]   #get the constant
            for i in range(16-len(const)):
                const = '0'+const
            b_c.append(op+rd+rs+const)

        elif temp[0].lower() == 'srl':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rs = '00000'
            rt = register((temp[1].lower().split(','))[1])
            rd = register((temp[1].lower().split(','))[0])
            shamt = bin(int((temp[1].lower().split(','))[2]))[2:]
            for i in range(5-len(shamt)):
                shamt = '0'+shamt
            function = '000010'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'bne':
            if temp[1].lower().split(',')[1].isnumeric(): #whether the second operator number is a constant
                content_code.append('addi $at,$zero,'+(temp[1].lower().split(','))[1])
                address.append(pc)
                pc += 4
                if labels_position[temp[1].lower().split(',')[2]] < len(content_code):
                    labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 2
                else:
                    labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 1
                #addi part
                op = '001000'
                rd = register('$zero')
                rs = register('$at')
                const = bin(int((temp[1].lower().split(','))[1]))[2:]
                for i in range(16-len(const)):
                    const = '0'+const
                b_c.append(op+rd+rs+const)

                #bne part
                content_code.append('bne '+(temp[1].lower().split(','))[0]+',$at,'+temp[1].lower().split(',')[2])
                op = '000101'
                rs = register((temp[1].lower().split(','))[0])
                rt = register('$at')
                #put in the addi part because of variable i # labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - i - 2
                address_offset = decToBin(labels[temp[1].lower().split(',')[2]])
                b_c.append(op+rt+rs+address_offset)

            else:                                                           #the second operator number is not a constant
                content_code.append((temp[0].lower())+' '+(temp[1].lower()))
                if labels_position[temp[1].lower().split(',')[2]] < len(content_code):
                    labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 2
                else:
                    labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 1
                op = '000101'
                rs = register((temp[1].lower().split(','))[0])
                rt = register((temp[1].lower().split(','))[2])
                address_offset = decToBin(labels[temp[1].lower().split(',')[2]])
                b_c.append(op+rt+rs+address_offset)

        #extra part
        elif temp[0].lower() == 'beq':
            if temp[1].lower().split(',')[1].isnumeric(): #whether the second operator number is a constant
                content_code.append('addi $at,$zero,'+(temp[1].lower().split(','))[1])
                address.append(pc)
                pc += 4
                if labels_position[temp[1].lower().split(',')[2]] < len(content_code):
                    labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 2
                else:
                    labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 1
                #addi part
                op = '001000'
                rd = register('$zero')
                rs = register('$at')
                const = bin(int((temp[1].lower().split(','))[1]))[2:]
                for i in range(16-len(const)):
                    const = '0'+const
                b_c.append(op+rd+rs+const)

                #bne part
                content_code.append('beq '+(temp[1].lower().split(','))[0]+',$at,'+temp[1].lower().split(',')[2])
                op = '000100'
                rs = register((temp[1].lower().split(','))[0])
                rt = register('$at')
                #put in the addi part because of variable i # labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - i - 2
                address_offset = decToBin(labels[temp[1].lower().split(',')[2]])
                b_c.append(op+rt+rs+address_offset)

            else:                                                       #the second operator number is not a constant
                content_code.append((temp[0].lower())+' '+(temp[1].lower()))
                if labels_position[temp[1].lower().split(',')[2]] < len(content_code):
                    labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 2
                else:
                    labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 1
                op = '000100'
                rs = register((temp[1].lower().split(','))[0])
                rt = register((temp[1].lower().split(','))[2])
                address_offset = decToBin(labels[temp[1].lower().split(',')[2]])
                b_c.append(op+rt+rs+address_offset)

        # elif temp[0].lower() == 'bge':
        #
        #     if temp[1].lower().split(',')[1].isnumeric(): #whether the second operator number is a constant
        #         content_code.append('slti $at,'+(temp[1].lower().split(','))[0]+','+(temp[1].lower().split(','))[1])
        #         address.append(pc)
        #         pc += 4
        #         if labels_position[temp[1].lower().split(',')[2]] < len(content_code):
        #             labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 2
        #         else:
        #             labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c) - 1
        #         #slti part
        #         op = '001000'
        #         rd = register('$zero')
        #         rs = register('$at')
        #         const = bin(int((temp[1].lower().split(','))[1]))[2:]
        #         for i in range(16-len(const)):
        #             const = '0'+const
        #         b_c.append(op+rd+rs+const)
        #
        #         #bne part
        #         content_code.append('bge $at,$zero,'+temp[1].lower().split(',')[2])
        #         op = '000100'
        #         rs = '00000'
        #         rt = register('$at')
        #         #put in the addi part because of variable i # labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - i - 2
        #         address_offset = decToBin(labels[temp[1].lower().split(',')[2]])
        #         b_c.append(op+rt+rs+address_offset)
        #
        #     else:                                                       #the second operator number is not a constant
        #         address.append(pc)
        #         pc += 4
        #         #slt parts
        #         content_code.append('slt $at,'+(temp[1].lower().split(','))[0]+','+(temp[1].lower().split(','))[1])
        #         op = '000000'
        #         rd = register('$at')          #get the destination register
        #         rs = register((temp[1].lower().split(','))[0])          #get the operator number 1 register
        #         rt = register((temp[1].lower().split(','))[1])          #get the operator number 2 register
        #         shamt = '00000'
        #         function = '101010'
        #         b_c.append(op+rs+rt+rd+shamt+function)
        #
        #
        #         for key in labels_position.keys():
        #             if labels_position[key] > i+move:
        #                 labels_position[key] += 1
        #         move += 1
        #         content_code.append((temp[0].lower())+' '+(temp[1].lower()))
        #         if labels_position[temp[1].lower().split(',')[2]] < len(content_code):
        #             labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c)
        #         else:
        #             labels[temp[1].lower().split(',')[2]] = labels_position[temp[1].lower().split(',')[2]] - len(b_c)
        #         # print(labels)
        #         op = '000100'
        #         rs = register('$zero')
        #         rt = register('$at')
        #         address_offset = decToBin(labels[temp[1].lower().split(',')[2]])
        #         while len(address_offset)!=16:
        #             address_offset = '0'+address_offset
        #         b_c.append(op+rt+rs+address_offset)

        elif temp[0].lower() == 'lui':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '001111'
            rd = '00000'
            rt = register(temp[1].lower().split(',')[0])
            data = bin(int(temp[1].lower().split(',')[1]))[2:]
            while len(data)!=16:
                data = '0'+data
            b_c.append(op+rd+rt+data)

        elif temp[0].lower() == 'and':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            shamt = '00000'
            function = '100100'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'or':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            shamt = '00000'
            function = '100101'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'xor':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            shamt = '00000'
            function = '100110'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'nor':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            shamt = '00000'
            function = '100111'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'slt':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            shamt = '00000'
            function = '101010'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'sltu':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            shamt = '00000'
            function = '101011'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'sll':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rs = '00000'
            rt = register((temp[1].lower().split(','))[1])          #get the operator 1 register
            rd = register((temp[1].lower().split(','))[0])          #get the operator 2 register
            shamt = bin(int((temp[1].lower().split(','))[2]))[2:]
            for i in range(5-len(shamt)):
                shamt = '0'+shamt
            function = '000000'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'sra':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rs = '00000'
            rt = register((temp[1].lower().split(','))[1])          #get the operator 1 register
            rd = register((temp[1].lower().split(','))[0])          #get the operator 2 register
            shamt = bin(int((temp[1].lower().split(','))[2]))[2:]
            for i in range(5-len(shamt)):
                shamt = '0'+shamt
            function = '000011'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'sllv':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            shamt = '00000'
            function = '000100'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'srlv':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            shamt = '00000'
            function = '000110'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'srav':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = register((temp[1].lower().split(','))[0])          #get the destination register
            rs = register((temp[1].lower().split(','))[1])          #get the operator number 1 register
            rt = register((temp[1].lower().split(','))[2])          #get the operator number 2 register
            shamt = '00000'
            function = '000111'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'j':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000010'
            if labels_position[temp[1].lower()]>=len(address):
                address_offset = bin((address[len(address)-1]+4)>>2)[2:]
            else:
                address_offset = bin(address[labels_position[temp[1].lower()]]>>2)[2:]
            while len(address_offset)!=26:
                address_offset = '0'+address_offset
            b_c.append(op+address_offset)

        elif temp[0].lower() == 'jr':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000000'
            rd = '00000'
            rs = register((temp[1].lower().split(','))[0])          #get the operator number 1 register
            rt = '00000'
            shamt = '00000'
            function = '001000'
            b_c.append(op+rs+rt+rd+shamt+function)

        elif temp[0].lower() == 'jal':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '000011'
            if labels_position[temp[1].lower()]>=len(address):
                address_offset = bin((address[len(address)-1]+4)>>2)[2:]
            else:
                address_offset = bin(address[labels_position[temp[1].lower()]]>>2)[2:]
            while len(address_offset)!=26:
                address_offset = '0'+address_offset
            b_c.append(op+address_offset)

        elif temp[0].lower() == 'andi':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '001100'
            rd = register((temp[1].lower().split(','))[1])          #get the source
            rs = register((temp[1].lower().split(','))[0])          #get the destination
            const = bin(int((temp[1].lower().split(','))[2]))[2:]   #get the constant
            for i in range(16-len(const)):
                const = '0'+const
            b_c.append(op+rd+rs+const)

        elif temp[0].lower() == 'ori':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '001101'
            rd = register((temp[1].lower().split(','))[1])          #get the source
            rs = register((temp[1].lower().split(','))[0])          #get the destination
            const = bin(int((temp[1].lower().split(','))[2]))[2:]   #get the constant
            for i in range(16-len(const)):
                const = '0'+const
            b_c.append(op+rd+rs+const)

        elif temp[0].lower() == 'xori':
            content_code.append((temp[0].lower())+' '+(temp[1].lower()))
            op = '001110'
            rd = register((temp[1].lower().split(','))[1])          #get the source
            rs = register((temp[1].lower().split(','))[0])          #get the destination
            const = bin(int((temp[1].lower().split(','))[2]))[2:]   #get the constant
            for i in range(16-len(const)):
                const = '0'+const
            b_c.append(op+rd+rs+const)

    print('The bytecode of the program is:')
    #print the bytecode
    for i in range(len(b_c)):
        tempStr1 = hex(int(address[i]))
        tempStr2 = hex(int(b_c[i],2))
        while len(tempStr1)!=10 or len(tempStr2)!=10:
            if len(tempStr1)!=10:
                tempStr1 = list(tempStr1)
                tempStr1.insert(2,'0')
                tempStr1 = ''.join(tempStr1)
            if len(tempStr2)!=10:
                tempStr2 = list(tempStr2)
                tempStr2.insert(2,'0')
                tempStr2 = ''.join(tempStr2)
        print(tempStr1,tempStr2)
    print("_______________________________")


    #excute the bytecode
    count = 0
    while count<len(b_c):
        #output run which sentence
        tempStr1 = hex(int(address[count]))
        tempStr2 = hex(int(b_c[count],2))
        while len(tempStr1)!=10 or len(tempStr2)!=10:
            if len(tempStr1)!=10:
                tempStr1 = list(tempStr1)
                tempStr1.insert(2,'0')
                tempStr1 = ''.join(tempStr1)
            if len(tempStr2)!=10:
                tempStr2 = list(tempStr2)
                tempStr2.insert(2,'0')
                tempStr2 = ''.join(tempStr2)
        print('Executing: '+tempStr1+"  "+tempStr2)

        # print(b_c[count][0:6],b_c[count][6:11],b_c[count][11:16],b_c[count][16:21],b_c[count][21:26],b_c[count][26:32])
        temp = content_code[count].split(' ')
        for j in range(temp.count('')):
            temp.remove('')

        if b_c[count][0:6] == '000000' and b_c[count][26:32] == '100000':#add
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][6:11],2)] + dic_register[int(b_c[count][11:16],2)]

        elif b_c[count][0:6] == '001000':#addi
            dic_register[int(b_c[count][11:16],2)] = dic_register[int(b_c[count][6:11],2)] + int(b_c[count][16:32],2)

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '000010':#srl
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][11:16],2)] >> int(b_c[count][21:26],2)

        elif b_c[count][0:6] == '000101': #bne
            if dic_register[int(b_c[count][11:16],2)] != dic_register[int(b_c[count][6:11],2)]:  #go to the specail label
                if labels_position[temp[1].lower().split(',')[2]]>count:
                    count = labels_position[temp[1].lower().split(',')[2]]
                else:
                    count = labels_position[temp[1].lower().split(',')[2]]-1

        elif b_c[count][0:6] == '000100': #beq
            if dic_register[int(b_c[count][11:16],2)] == dic_register[int(b_c[count][6:11],2)]:  #go to the specail label
                if labels_position[temp[1].lower().split(',')[2]]>count:
                    count = labels_position[temp[1].lower().split(',')[2]]
                else:
                    count = labels_position[temp[1].lower().split(',')[2]]-1
        #
        # elif temp[0].lower() == 'bge':
        #     rs = register('$at')
        #     rt = register('$zero')
        #     #calc the value of registers
        #     if dic_register[int(rs,2)] >= dic_register[int(rt,2)]:  #go to the specail label
        #         if labels_position[temp[1].lower().split(',')[2]]>count:
        #             count = labels_position[temp[1].lower().split(',')[2]]
        #         else:
        #             count = labels_position[temp[1].lower().split(',')[2]]-1
        #
        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '100100': #and
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][6:11],2)] & dic_register[int(b_c[count][11:16],2)]

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '100101': #or
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][6:11],2)] | dic_register[int(b_c[count][11:16],2)]

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '100110': #xor
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][6:11],2)] ^ dic_register[int(b_c[count][11:16],2)]

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '100111': #nor
            dic_register[int(b_c[count][16:21],2)] = ~(dic_register[int(b_c[count][6:11],2)] | dic_register[int(b_c[count][11:16],2)])

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '101010': #slt
            if dic_register[int(b_c[count][6:11],2)] < dic_register[int(b_c[count][11:16],2)]:
                dic_register[int(b_c[count][16:21],2)] = 1
            else:
                dic_register[int(b_c[count][16:21],2)] = 0

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '101011': #sltu
            if dic_register[int(b_c[count][6:11],2)] < dic_register[int(b_c[count][11:16],2)]:
                dic_register[int(b_c[count][16:21],2)] = 1
            else:
                dic_register[int(b_c[count][16:21],2)] = 0


        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '000000': #sll
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][11:16],2)] << int(b_c[count][21:26],2)

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '000011': #sra
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][11:16],2)] >> int(b_c[count][21:26],2)

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '000100': #sllv
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][6:11],2)] << dic_register[int(b_c[count][11:16],2)]

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '000110': #srlv
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][6:11],2)] >> dic_register[int(b_c[count][11:16],2)]

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '000111': #srav
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][6:11],2)] >> dic_register[int(b_c[count][11:16],2)]

        elif b_c[count][0:6] == '000010': #j
            count = labels_position[temp[1].lower()]

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '001000': #jr
            count = address.index(address[dic_register[int(b_c[count][11:16],2)]])

        elif b_c[count][0:6] == '000011': #jal
            count = labels_position[temp[1].lower()]
            dic_register[31] = address[count+1]

        elif b_c[count][0:6] == '001100': #andi
            dic_register[int(b_c[count][11:16],2)] = dic_register[int(b_c[count][6:11],2)] & int(b_c[count][16:32],2)

        elif b_c[count][0:6] == '001101': #ori
            dic_register[int(b_c[count][11:16],2)] = dic_register[int(b_c[count][6:11],2)] | int(b_c[count][16:32],2)

        elif b_c[count][0:6] == '001110': #xori
            dic_register[int(b_c[count][11:16],2)] = dic_register[int(b_c[count][6:11],2)] ^ int(b_c[count][16:32],2)

        elif b_c[count][0:6] == '000000' and b_c[count][26:32] == '100010': #sub
            dic_register[int(b_c[count][16:21],2)] = dic_register[int(b_c[count][6:11],2)] - dic_register[int(b_c[count][11:16],2)]

        elif b_c[count][0:6] == '001111': #lui
            dic_register[int(b_c[count][11:16],2)] = int(b_c[count][16:32],2)<<16

        else:
            pass
        count += 1

if __name__ == '__main__':
    logo = '''
______________________________________________________________________________________
    ╭╭╮╮╭──╮╭──╮╭──╮    ╭──╮╭╮╭╮╭──╮╭╮╭╮╭──╮╭╮╭╮
    │　│╰╮╭╯│╭╮││╭─╯　  │╭╮││╰╯│╰╮╭╯│││││╭╮││╰╮│
    ││││ ││ │╰╯││╰─╮　  │╰╯│╰╮╭╯ ││ │╰╯││││││　│
    │╭╮│ ││ │╭─╯╰─╮│　  │╭─╯ ││　││ │╭╮││││││　│
    ││││╭╯╰╮││　╭─╯│    ││　 ││　││ │││││╰╯││╰╮│
    ╰╯╰╯╰──╯╰╯　╰──╯    ╰╯　 ╰╯　╰╯ ╰╯╰╯╰──╯╰╯╰╯　

    ╭──╮╭╮╭╮　╭──╮╭──╮╭──╮
    │╭╮││╰╯│　│╭╮│╰─╮│╰─╮│
    │╰╯╯╰╮╭╯　│╰╯│ ╭╯╯ ╭╯╯
    │╭╮╮ ││　 │╭─╯╭╯╯ ╭╯╯　
    │╰╯│ ││　 ││　│╰─╮│╰─╮
    ╰──╯ ╰╯　 ╰╯　╰──╯╰──╯
______________________________________________________________________________________
    '''
    print(logo)
    print('Pay attention to: this script can not support for using multiple labels to jump\n')
    print("You can use these instructions in the program: ")
    print("addi add srl bne beq lui and or xor nor slt sltu sll srl sra sllv srlv srav jr j jal andi ori xori\n")
    print('--------------------------------------------------------------------------------------------------')
    filename = input("Now please input your file path: ")
    get_content()
    bytecode()
    print('Register:')
    #give value of the $gp and $sp registers
    dic_register[28] = 268468224
    dic_register[29] = 2147479548

    #print values of each registers
    for i in dic_register.keys():
        print(str(i)+": "+str(int(dic_register[i])))
    tempPc = hex(pc)

    #ensure the output is beatiful
    while len(tempPc)!=10:
        tempPc = list(tempPc)
        tempPc.insert(2,'0')
        tempPc = ''.join(tempPc)
    print("Program counter: "+tempPc)
    print("...DONE!")
