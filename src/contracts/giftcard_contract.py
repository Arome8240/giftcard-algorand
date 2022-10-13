from pyteal import *


class GiftCard:
    class Variables:
        number = Bytes("NUMBER")
        description = Bytes("DESCRIPTION")
        image = Bytes("IMAGE")
        amount = Bytes("AMOUNT")
        bought = Bytes("BOUGHT")
        current_owner = Bytes("OWNER")

    class AppMethods:
        buy = Bytes("buy")
        sell = Bytes("sell")

    # allow users to create a new gift card application
    def application_creation(self):
        return Seq([
            Assert(
                # run the following checks that:
                And(
                    # The number of arguments attached to the transaction should be exactly 4.
                    Txn.application_args.length() == Int(4),
                    # The note attached to the transaction must be "giftcard:uv3".
                    Txn.note() == Bytes("giftcard:uv3"),
                    # The giftcard price is greater than 0
                    Btoi(Txn.application_args[3]) > Int(0),
                )
            ),
            App.globalPut(self.Variables.number, Txn.application_args[0]),
            App.globalPut(self.Variables.description, Txn.application_args[1]),
            App.globalPut(self.Variables.image, Txn.application_args[2]),
            App.globalPut(self.Variables.amount,
                          Btoi(Txn.application_args[3])),
            App.globalPut(self.Variables.bought, Int(0)),
            App.globalPut(self.Variables.current_owner, Txn.accounts[0]),
            Approve()
        ])

    # allow users to buy a gift card that hasn't been bought yet
    def buyCard(self):
        return Seq([
            Assert(
                # run the following checks that:
                And(
                    # The transaction group is made up of 2 transactions
                    Global.group_size() == Int(2),
                    # The buyCard txn is made ahead of the payment transaction
                    Txn.group_index() == Int(0),
                    # The item hasn't been bought
                    App.globalGet(self.Variables.bought) == Int(0),
                    # The sender of transaction is not the giftcard owner
                    App.globalGet(
                        self.Variables.current_owner) != Txn.sender(),
                ),
            ),
            Assert(
                # checks for the payment transaction
                And(
                    Gtxn[1].type_enum() == TxnType.Payment,
                    Gtxn[1].receiver() == App.globalGet(
                        self.Variables.current_owner),
                    Gtxn[1].amount() == App.globalGet(self.Variables.amount),
                    Gtxn[1].sender() == Gtxn[0].sender(),
                )
            ),

            App.globalPut(self.Variables.current_owner, Txn.accounts[0]),
            App.globalPut(self.Variables.amount, App.globalGet(
                self.Variables.amount) * Int(2)),
            App.globalPut(self.Variables.bought, Int(1)),
            Approve()
        ])

    # allow gift cards' owners to sell their gift cards
    def sellGiftCard(self):
        Assert(
            # run the following checks that:
            And(
                # The gift card is already bought
                App.globalGet(self.Variables.bought) == Int(1),
                # The sender is the gift card's owner
                App.globalGet(
                    self.Variables.current_owner) == Txn.sender(),
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
