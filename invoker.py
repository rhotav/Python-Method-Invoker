import clr
from System.Reflection import Assembly, MethodInfo, BindingFlags
from System import Type


def Save():
    module.Write("deobfuscated.exe")


def MethodIdentifier():
    global stringMethodName
    global invokeMethod
    eFlags = BindingFlags.Static | BindingFlags.Public | BindingFlags.NonPublic
    for type in module.Types:
        for method in type.Methods:
            if not method.HasBody: pass
            if len(method.Body.Instructions) < 107: pass
            i = 0
            while i < len(method.Body.Instructions):
                if(method.Body.Instructions[i].IsLdcI4() and
                     method.Body.Instructions[i + 2].OpCode == OpCodes.Ldsfld):
                    stringMethodName = str(method.Name)
                    stringTypeName = str(type.Name)
                    for types in assembly.GetTypes():
                        if types.Name == stringTypeName:
                            classInstance = types
                            break

                    for methods in classInstance.GetMethods(eFlags):
                        if methods.Name == stringMethodName:
                            invokeMethod = methods
                            return
                    break
                i += 1


def DecryptStrings():
    decryptedStrings = 0
    for type in module.Types:
        if not type.HasMethods: pass
        
        for method in type.Methods:
            if not method.HasBody: pass
            i = 0
            operText = ""
            while i < len(method.Body.Instructions):
                operText = str(method.Body.Instructions[i].Operand).encode()
                if(method.Body.Instructions[i].OpCode == OpCodes.Call and
                        operText.find(str(stringMethodName).encode()) != -1):
                    keyValue = method.Body.Instructions[i - 1].GetLdcI4Value()
                    result = str(invokeMethod.Invoke(None, [keyValue]))
                    method.Body.Instructions[i - 1].OpCode = OpCodes.Nop
                    method.Body.Instructions[i].OpCode = OpCodes.Ldstr
                    method.Body.Instructions[i].Operand = result
                    decryptedStrings += 1
                i += 1
    print("Decrypted {} string".format(decryptedStrings))


if __name__ == "__main__":
    clr.AddReference(r"DNLIB PATH")
    import dnlib
    from dnlib.DotNet.Emit import OpCodes
    global module
    global assembly
    module = dnlib.DotNet.ModuleDefMD.Load("WindowsFormsApp3.exe")
    assembly = Assembly.LoadFrom("WindowsFormsApp3.exe")
    DecryptStrings()
    Save()
