from pyteal import *


class GiftCard:
    class GlobalVariables:
        description = Bytes("DESCRIPTION")
        image = Bytes("IMAGE")
        amount = Bytes("AMOUNT")
        activated = Bytes("ACTIVATED")
        bought = Bytes("BOUGHT")
        current_owner = Bytes("OWNER")

    class AppMethods:
        activate = Bytes("activate")
        buy = Bytes("buy")
        gift = Bytes("gift")
        sell = Bytes("sell")

    class LocalVariables:
        number = Bytes("NUMBER")

    # allow users to create a new gift card application
    def application_creation(self):
        return Seq([
            Assert(
                # run the following checks that:
                And(
                    # The number of arguments attached to the transaction should be exactly 3.
                    Txn.application_args.length() == Int(3),
                    # The note attached to the transaction must be "giftcard:uv3".
                    Txn.note() == Bytes("giftcard:uv3"),
                    # The giftcard price is greater than 0
                    Btoi(Txn.application_args[3]) > Int(0),
                )
            ),
            App.globalPut(self.GlobalVariables.description,
                          Txn.application_args[0]),
            App.globalPut(self.GlobalVariables.image, Txn.application_args[1]),
            App.globalPut(self.GlobalVariables.amount,
                          Btoi(Txn.application_args[2])),
            App.globalPut(self.GlobalVariables.activated, Int(0)),
            App.globalPut(self.GlobalVariables.bought, Int(0)),
            App.globalPut(self.GlobalVariables.current_owner, Txn.accounts[0]),
            Approve()
        ])

    # opt in to contract
    def optIn(self):
        return Approve()

    # allow user to activate the gift card and input the gift card number
    def activate_gift_card(self):
        return Seq([
            Assert(
                # run the following checks that:
                And(
                    # that user has opted in
                    App.optedIn(Txn.accounts[0], Txn.applications[0]),
                    # The number of arguments attached to the transaction should be exactly 2.
                    Txn.application_args.length() == Int(2),
                    # The gift card has not been acutivated
                    App.globalGet(self.GlobalVariables.activated) == Int(0),
                    # The sender is the giftcard creator
                    Txn.sender() == Global.creator_address()
                ),
            ),
            # store giftcard number in user local state
            App.localPut(
                Txn.accounts[0], self.LocalVariables.number, Txn.application_args[1]),
            # set giftcard as activated
            App.globalPut(self.GlobalVariables.activated, Int(1)),
            Approve()
        ])

    # allow users to send a gift card to another user
    def gift_card(self):
        gift_card_number = App.localGet(
            Txn.accounts[0], self.LocalVariables.number)
        return Seq([
            Assert(
                # run the following checks that:
                And(
                    # that owner has opted in
                    App.optedIn(Txn.accounts[0], Txn.applications[0]),
                    # The accounts array is not empty
                    Txn.accounts.length() == Int(1),
                    # that receiver has opted in
                    App.optedIn(Txn.accounts[1], Txn.applications[0]),
                    # The gift card has been activated
                    App.globalGet(self.GlobalVariables.activated) == Int(1),
                    # The sender is the giftcard owner
                    Txn.sender() == App.globalGet(self.GlobalVariables.current_owner),
                ),
            ),
            # store giftcard number in receiver's local state
            App.localPut(
                Txn.accounts[1], self.LocalVariables.number, gift_card_number),

            # delete giftcard number from owner's local state
            App.localDel(Txn.accounts[0], self.LocalVariables.number),

            # store receiver's address as current owner
            App.globalPut(
                self.GlobalVariables.current_owner, Txn.accounts[1]),

            Approve()
        ])

    # allow users to buy a gift card that hasn't been bought yet
    def buy_card(self):
        current_owner = App.globalGet(
            self.GlobalVariables.current_owner)

        # sequence that checks current owner's state for giftcard
        check_giftcard_number = App.localGetEx(
            Txn.accounts[1], Txn.applications[0], self.LocalVariables.number)
        return Seq([
            Assert(
                # run the following checks that:
                And(
                    # that user has opted in
                    App.optedIn(Txn.accounts[0], Txn.applications[0]),
                    # The transaction group is made up of 2 transactions
                    Global.group_size() == Int(2),
                    # The buyCard txn is made ahead of the payment transaction
                    Txn.group_index() == Int(0),
                    # The accounts array is not empty
                    Txn.accounts.length() == Int(1),
                    # The address passed in is the current owner of gift card
                    Txn.accounts[1] == current_owner,
                    # The gift card has not been activated
                    App.globalGet(self.GlobalVariables.activated) == Int(1),
                    # The gift card hasn't been bought
                    App.globalGet(self.GlobalVariables.bought) == Int(0),
                    # The sender of transaction is not the giftcard owner
                   current_owner != Txn.sender(),
                   ),
            ),
            Assert(
                # checks for the payment transaction
                And(
                    Gtxn[1].type_enum() == TxnType.Payment,
                    Gtxn[1].receiver() == App.globalGet(
                        self.GlobalVariables.current_owner),
                    Gtxn[1].amount() == App.globalGet(
                        self.GlobalVariables.amount),
                    Gtxn[1].sender() == Gtxn[0].sender(),
                )
            ),

            # check for giftcard number in current owner's local state
            check_giftcard_number,

            # if check returns a value
            If(check_giftcard_number.hasValue())
            .Then(
                Seq([
                    # store giftcard number in txn sender's local state
                    App.localPut(
                        Txn.accounts[0], self.LocalVariables.number, check_giftcard_number.value()),

                    # delete giftcard number from previous owner's local state
                    App.localDel(Txn.accounts[1], self.LocalVariables.number),

                    # store txn sender's address as current owner
                    App.globalPut(
                        self.GlobalVariables.current_owner, Txn.accounts[0]),

                    # update amount
                    App.globalPut(self.GlobalVariables.amount, App.globalGet(
                        self.GlobalVariables.amount) * Int(2)),

                    # set giftcard as bought
                    App.globalPut(self.GlobalVariables.bought, Int(1)),
                    Approve()
                ])
            )
            .Else(
                Reject()
            ),
        ])

    # allow gift cards' owners to sell their gift cards
    def sell_gift_card(self):
        return Seq([
            Assert(
                # run the following checks that:
                And(
                    # The gift card is already bought
                    App.globalGet(self.GlobalVariables.bought) == Int(1),
                    # The sender is the gift card's owner
                    App.globalGet(
                        self.GlobalVariables.current_owner) == Txn.sender(),
                ),
            ),
            App.globalPut(self.GlobalVariables.bought, Int(0)),
            Approve()
        ])

    def application_deletion(self):
        return Return(Txn.sender() == Global.creator_address())

    def application_start(self):
        return Cond(
            [Txn.application_id() == Int(0), self.application_creation()],
            [Txn.on_completion() == OnComplete.DeleteApplication,
             self.application_deletion()],
            [Txn.on_completion() == OnComplete.OptIn, self.optIn()],
            [Txn.application_args[0] == self.AppMethods.activate,
                self.activate_gift_card()],
            [Txn.application_args[0] == self.AppMethods.buy, self.gift_card()],
            [Txn.application_args[0] == self.AppMethods.buy, self.buy_card()],
            [Txn.application_args[0] == self.AppMethods.sell, self.sell_gift_card()],
        )

    def approval_program(self):
        return self.application_start()

    def clear_program(self):
        return Return(Int(1))
