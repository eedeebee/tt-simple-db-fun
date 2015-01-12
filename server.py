#!/usr/bin/python
"""
See http://www.thumbtack.com/challenges/simple-database
"""

import sys

class DB:
    """
    The DB class is an implementation of the Simple DB Challenge as described by 
    Thumbtack and referenced above.  This implementation assumes a single 
    synchronous client, which avoids concurrency issues that might 
    arise with the specified transaction behavior.

    The implementation uses two python dictionaries to hold the data.
    One that stores the names and values and another that keeps track of
    any values in use and their current counts.  A value of None
    represents an item that was SET at one point and is currently
    UNSET.

    Transactions are supported by nesting DBs - creating a new
    fresh DB for each transaction and then updating and maintaining
    it during the transaction on an ad hoc/as needed basis.  Rollbacks simply 
    trash the transient state.  And a commit updates the parent DB  (and its parents...)
    based on current state in the child.

    All DB operations are constant time, O(1) on the number of variables in the DB.
    Transactions use limited memory (linear based on the number of variables used in the
    transaction).

    """
    def __init__(self, parent):
        self.names = {}
        self.values = {}
        self.parent = parent # None means this is the root DB

    def __getValue(self, name):
        """ return get value for name, avoiding transactions"""
        if name in self.names:
            return self.names[name]
        else:
            # If I don't have a name, check my parent
            if self.parent:
                return self.parent.__getValue(name)
            else:
                return None

    def __getCount(self, value):
        """ return get count for value, avoiding transactions"""
        if value in self.values:
            return self.values[value]
        else:
            # If I don't have a value, check my parent
            if self.parent:
                return self.parent.__getCount(value)
            else:
                return 0

    def __merge(self, db):
        """ Update internal values and counts based on given db """
        for name, value in db.names.iteritems():
            self.names[name] = value
        for value, count in db.values.iteritems():
            self.values[value] = count

    def __copyValueFromParent(self, name):
        """ Copy value from parent """
        parentValue = self.parent.__getValue(name)
        if parentValue:
            self.names[name] = parentValue
            if parentValue not in self.values:
                parentCount = self.parent.__getCount(parentValue)
                self.values[parentValue] = parentCount

    def SET(self, args):
        """
        Remove any existing value for the name and decrement the count of that old value.
        Set the new value and update the count of the new value
        """ 
        if len(args) != 3:
            return "Syntax error: " + " ".join(args)

        name = args[1]
        value = args[2]

        # Consider we might be in a transaction.  Copy in to this DB everything we need 
        # from the parent to provide accurate responses.
        if self.parent:
            # if current db doesn't knows about this name or current value, get details from parent db
            if name not in self.names:
                self.__copyValueFromParent(name)
                    
            # if current db doesn't know about the new value, get details from parent db
            if value not in self.values:
                self.values[value] = self.parent.__getCount(value)

        if name in self.names:
            curvalue = self.names[name]
            if curvalue != None:
                self.values[curvalue] -= 1

        self.names[name] = value
        if value not in self.values or self.values[value] == None:
            self.values[value] = 1
        else:
            self.values[value] += 1

        return ""

    def UNSET(self, args):
        """
        Remove any existing value of the name and decrement the count of that old value
        """
        if len(args) != 2:
            return "Syntax error: " + " ".join(args)

        name = args[1]

        # Consider we might be in a transaction
        if self.parent:
            # if current db doesn't knows about this name or current value, get details from parent db
            if name not in self.names:
                self.__copyValueFromParent(name)

        if name in self.names:
            curvalue = self.names[name]
            if curvalue != None:
                self.values[curvalue] -= 1
                self.names[name] = None
        else:
            ## Be lenient and just silence the error
            ## return "No name : " + name
            return ""

        return ""


    def GET(self, args):
        if len(args) != 2:
            return "Syntax error: " + " ".join(args)
            

        name = args[1]
        if name in self.names:
            if self.names[name] == None:
                return "NULL"
            else:
                return self.names[name]
        else:
            ## current db doesn't know about this name, get details from parent db
            if self.parent:
                return self.parent.GET(args)
            else:
                return "NULL" 

    def NUMEQUALTO(self, args):
        
        if len(args) != 2:
            return "Syntax error: " + " ".join(args)

        value = args[1]
        if value in self.values:
            return self.values[value]
        else:
            ## current db doesn't know about this value, get details from parent db
            if self.parent:
                return self.parent.NUMEQUALTO(args)
            else:
                return 0

    def BEGIN(self, line):
        """
        return a new db that is parent of me
        """
        return "", DB(self)

    def ROLLBACK(self, line):
        """ 
        return my parent db
        """
        if self.parent:
            return "", self.parent
        else:
            return "NO TRANSACTION"

    def COMMIT(self, line):
        """
        Merge our data into our parent and then "recurse" to our parent.
        Return the last root db.
        """
        if self.parent:
            db = self
            while 1:
                db.parent.__merge(self)
                db = db.parent
                if db.parent == None: 
                    break

            return "", db
        else:
            return "NO TRANSACTION"


curdb = DB(None)

while 1:
    try:
        line = raw_input()
    except (KeyboardInterrupt, EOFError):
        break
    else:
        args = line.split()

        # Handle empty lines
        if len(args) == 0:
            continue

        # Not in spec, but convenient for hand testing 
        cmd = args[0].upper() 

        # Special handling
        if cmd == 'END':
            print "";
            sys.exit(0)


        try :
            f = getattr(curdb, cmd)
        except (AttributeError):  # catches more than just unknown cmds :(`
            print "Unknown command " + cmd
        else:
            r = f(args)
            # Some commands return a new DB as well as the response
            if isinstance(r, tuple):
                print "\t" + str(r[0])
                curdb = r[1]
            else:
                print "\t" + str(r)

        sys.stdout.flush()

