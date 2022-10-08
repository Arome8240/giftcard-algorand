from pyteal import *

class GiftCard:
    class Variables:
        number = Bytes("NUMBER") # String variable representing the gift card's code
        description = Bytes("DESCRIPTION")
        image = Bytes("IMAGE")
        amount = Bytes("AMOUNT")
        bought = Bytes("BOUGHT")
        address = Bytes("ADDRESS")
        owner = Bytes("OWNER")

    class AppMethods:
        buy = Bytes("buy")
        sell = Bytes("sell")

    # allow users to create a new gift card application
    def application_creation(self):
        return Seq([
            # checks if input data contains only valid/non-empty input data
            Assert(
                And(            
                    Txn.application_args.length() == Int(5),
                    Txn.note() == Bytes("giftcard:uv2"),
                    Btoi(Txn.application_args[3]) > Int(0),
                    Len(Txn.application_args[0]) > Int(0),
                    Len(Txn.application_args[1]) > Int(0),
                    Len(Txn.application_args[2]) > Int(0),
                    Len(Txn.application_args[4]) > Int(0),
                )
            ),
            App.globalPut(self.Variables.number, Txn.application_args[0]),
            App.globalPut(self.Variables.description, Txn.application_args[1]),
            App.globalPut(self.Variables.image, Txn.application_args[2]),
            App.globalPut(self.Variables.amount, Btoi(Txn.application_args[3])),
            App.globalPut(self.Variables.bought, Int(0)),
            App.globalPut(self.Variables.address, Global.creator_address()),
            App.globalPut(self.Variables.owner, Txn.application_args[4]),
            Approve()
        ])
    
    # allow users to buy a gift card that hasn't been bought yet
    def buyCard(self):
        return Seq([
            Assert(
                # checks if gift card is available
                # checks if sender is not the gift card's seller/current owner
                # checks if the new value for owner is not empty
                And(
                    Global.group_size() == Int(2),
                    Txn.application_args.length() == Int(2),
                    App.globalGet(self.Variables.bought) == Int(0),
                    App.globalGet(self.Variables.address) != Txn.sender(),
                    Len(Txn.application_args[1]) > Int(0),
                ),
            ),
            Assert(
                And(
                    Gtxn[1].type_enum() == TxnType.Payment,
                    Gtxn[1].receiver() == App.globalGet(
                        self.Variables.address),
                    Gtxn[1].amount() == App.globalGet(self.Variables.amount),
                    Gtxn[1].sender() == Gtxn[0].sender(),
                )
            ),

            App.globalPut(self.Variables.owner, Txn.application_args[1]),
            App.globalPut(self.Variables.address, Gtxn[1].sender()),
            App.globalPut(self.Variables.amount, App.globalGet(self.Variables.amount) * Int(2)),
            App.globalPut(self.Variables.bought, Int(1)),
            Approve()
        ])
    # allow gift cards' owners to sell their gift cards
    def sellGiftCard(self):
        Assert(
            # checks if gift card is already bought
            # checks if sender is the gift card's owner
            And(
                Txn.application_args.length() == Int(2),
                App.globalGet(self.Variables.bought) == Int(1),
                App.globalGet(
                    self.Variables.owner) == Txn.application_args[1],
                App.globalGet(self.Variables.address) == Txn.sender(),
            ),
        )

        return Seq([
            App.globalPut(self.Variables.bought, Int(0)),
            Approve()
        ])

    def application_deletion(self):
        return Return(Txn.sender() == Global.creator_address())

    def application_start(self):
        return Cond(
            [Txn.application_id() == Int(0), self.application_creation()],
            [Txn.on_completion() == OnComplete.DeleteApplication,
             self.application_deletion()],
            [Txn.application_args[0] == self.AppMethods.buy, self.buyCard()],
            [Txn.application_args[0] == self.AppMethods.sell, self.sellGiftCard()],
        )

    def approval_program(self):
        return self.application_start()

    def clear_program(self):
        return Return(Int(1))


        