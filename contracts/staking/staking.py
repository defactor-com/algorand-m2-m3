from pyteal import *
from pyteal.ast.bytes import Bytes
from pyteal_helpers import program

PERCENTAGE_MULTIPLIER = Int(100)
YEAR_IN_SECONDS = Int(31536000)

""" FACTR_TOKEN = Int(148773679)
USDC_TOKEN = Int(10458941) """
FACTR_TOKEN = Int(984420777)
USDC_TOKEN = Int(31566704)

PLANS = [
    # USDC PLANS
    {
        "stakeEndTime": Int(1680264000),
        "minStakeAmount": Int(10 * 1_000_000),
        "lockDuration": Int(86400 * 30),
        "apy": Int(4),
        "assetId": USDC_TOKEN,
        "secondaryRewardAssetId": FACTR_TOKEN,
        "secondaryRewardPerToken": Int(int(2 * 1_000_000)),
        "rewardAssetId": Int(984724054),
    },
    {
        "stakeEndTime": Int(1680264000),
        "minStakeAmount": Int(10 * 1_000_000),
        "lockDuration": Int(86400 * 90),
        "apy": Int(6),
        "assetId": USDC_TOKEN,
        "secondaryRewardAssetId": FACTR_TOKEN,
        "secondaryRewardPerToken": Int(int(6 * 1_000_000)),
        "rewardAssetId": Int(984724521),
    },

    # FACTR PLANS
    {
        "stakeEndTime": Int(1680264000),
        "minStakeAmount": Int(4000 * 1_000_000),
        "lockDuration": Int(86400 * 30),
        "apy": Int(16),
        "assetId": FACTR_TOKEN,
        "secondaryRewardAssetId": USDC_TOKEN,
        "secondaryRewardPerToken": Int(int(0.000417 * 1_000_000)),
        "rewardAssetId": Int(984725277),
    },
    {
        "stakeEndTime": Int(1680264000),
        "minStakeAmount": Int(4000 * 1_000_000),
        "lockDuration": Int(86400 * 90),
        "apy": Int(20),
        "assetId": FACTR_TOKEN,
        "secondaryRewardAssetId": USDC_TOKEN,
        "secondaryRewardPerToken": Int(int(0.001250 * 1_000_000)),
        "rewardAssetId": Int(984725788),
    },
]


def approval():
    # globals
    global_creator = Bytes("creator")  # byteslice

    # locals
    # byteslice - simulated int array
    local_stakePlanIds = Bytes("stakePlanIds")
    # byteslice - simulated int array
    local_stakeAmounts = Bytes("stakeAmounts")
    # byteslice - simulated int array
    local_stakeUnlocks = Bytes("stakeUnlocks")
    local_claimed = Bytes("claimed")  # byteslice - simulated int array

    # operations
    op_optinFT = Bytes("optinFT")
    op_withdraw = Bytes("withdraw")
    op_stake = Bytes("stake")
    op_unstake = Bytes("unstake")

    # push integer to array
    @Subroutine(TealType.none)
    def pushInt(array: Expr, value: TealType.uint64):
      s_array = ScratchVar(TealType.bytes)

      return Seq(
          s_array.store(
              Concat(
                  App.localGet(Txn.sender(), array),
                  Itob(value),
              ),
          ),
          App.localPut(
              Txn.sender(),
              array,
              s_array.load(),
          ),
      )

    # set integer at index
    @Subroutine(TealType.none)
    def setIntAt(array: Expr, index: Expr, value: TealType.uint64):
      s_array = ScratchVar(TealType.bytes)

      return Seq(
          s_array.store(App.localGet(Txn.sender(), array)),
          App.localPut(Txn.sender(), array, Concat(
              Substring(s_array.load(), Int(0), index * Int(8)),
              Itob(value),
              Substring(s_array.load(), (index + Int(1))
                        * Int(8), Len(s_array.load()))
          )),
      )

    # get integer at index
    @Subroutine(TealType.uint64)
    def intAt(array: Expr, index: Expr):
      return Return(
          Btoi(Extract(App.localGet(Txn.sender(), array), index * Int(8), Int(8)))
      )

    def getPlanProperty(planId, property):
      return [
          [planId == Int(0), PLANS[0][property]],
          [planId == Int(1), PLANS[1][property]],
          [planId == Int(2), PLANS[2][property]],
          [planId == Int(3), PLANS[3][property]],
      ]

    @Subroutine(TealType.uint64)
    def stakeEndTime(planId: Expr):
      return Return(Cond(*getPlanProperty(planId, "stakeEndTime")))

    @Subroutine(TealType.uint64)
    def minStakeAmount(planId: Expr):
      return Return(Cond(*getPlanProperty(planId, "minStakeAmount")))

    @Subroutine(TealType.uint64)
    def apy(planId: Expr):
      return Return(Cond(*getPlanProperty(planId, "apy")))

    @Subroutine(TealType.uint64)
    def assetId(planId: Expr):
      return Return(Cond(*getPlanProperty(planId, "assetId")))

    @Subroutine(TealType.uint64)
    def lockDuration(planId: Expr):
      return Return(Cond(*getPlanProperty(planId, "lockDuration")))

    @Subroutine(TealType.uint64)
    def secondaryRewardPerToken(planId: Expr):
      return Return(Cond(*getPlanProperty(planId, "secondaryRewardPerToken")))

    @Subroutine(TealType.uint64)
    def secondaryRewardAssetId(planId: Expr):
      return Return(Cond(*getPlanProperty(planId, "secondaryRewardAssetId")))

    @Subroutine(TealType.uint64)
    def rewardAssetId(planId: Expr):
      return Return(Cond(*getPlanProperty(planId, "rewardAssetId")))

    @Subroutine(TealType.none)
    def stake():
      planId = ScratchVar(TealType.uint64)

      return Seq(
          program.check_self(
              group_size=Int(2),
              group_index=Int(0),
          ),
          program.check_rekey_zero(2),
          Assert(Txn.application_args.length() == Int(2)),
          planId.store(Btoi(Txn.application_args[1])),
          Assert(
              And(
                  # check FT amount sent
                  Gtxn[1].type_enum() == TxnType.AssetTransfer,
                  Gtxn[1].asset_receiver() == Global.current_application_address(),
                  Gtxn[1].asset_close_to() == Global.zero_address(),

                  # check FT index
                  Gtxn[1].xfer_asset() == assetId(planId.load()),

                  # check stakeEnd time
                  stakeEndTime(planId.load()) >= Global.latest_timestamp(),

                  # check min stake amount
                  minStakeAmount(planId.load()) <= Gtxn[1].asset_amount()
              ),
          ),
          pushInt(local_stakePlanIds, planId.load()),
          pushInt(local_stakeAmounts, Gtxn[1].asset_amount()),
          pushInt(local_stakeUnlocks, Global.latest_timestamp() + \
                  lockDuration(planId.load())),
          pushInt(local_claimed, Int(0)),

          InnerTxnBuilder.Begin(),
          InnerTxnBuilder.SetFields({
              TxnField.type_enum: TxnType.AssetTransfer,
              TxnField.asset_receiver: Txn.sender(),
              TxnField.asset_amount: Int(1),
              TxnField.xfer_asset: rewardAssetId(planId.load()),
              TxnField.fee: Int(0),
          }),
          InnerTxnBuilder.Submit(),

          Approve(),
      )

    @Subroutine(TealType.uint64)
    def calculateMainReward(index: Expr, planId: Expr):
      return Return(
          intAt(local_stakeAmounts, index) +
          ((intAt(local_stakeAmounts, index) * apy(planId) * lockDuration(planId)) /
           (PERCENTAGE_MULTIPLIER * YEAR_IN_SECONDS))
      )

    @Subroutine(TealType.uint64)
    def calculateSecondaryReward(index: Expr, planId: Expr):
      return Return(
          intAt(local_stakeAmounts, index)
          / Int(1_000_000)
          * secondaryRewardPerToken(planId)
      )

    @Subroutine(TealType.none)
    def unstake():
      index = ScratchVar(TealType.uint64)
      mainReward = ScratchVar(TealType.uint64)
      secondaryReward = ScratchVar(TealType.uint64)
      planId = ScratchVar(TealType.uint64)

      return Seq(
          program.check_self(
              group_size=Int(1),
              group_index=Int(0),
          ),
          program.check_rekey_zero(1),
          Assert(Txn.application_args.length() == Int(2)),

          index.store(Btoi(Txn.application_args[1])),
          planId.store(intAt(local_stakePlanIds, index.load())),
          mainReward.store(calculateMainReward(index.load(), planId.load())),
          secondaryReward.store(calculateSecondaryReward(
              index.load(), planId.load())),

          Assert(
              And(
                  # check that fee is big enough
                  If(
                      Gt(secondaryReward.load(), Int(0)),
                      Txn.fee() >= Global.min_txn_fee() * Int(3),
                      Txn.fee() >= Global.min_txn_fee() * Int(2),
                  ),

                  # make sure stake at provided index can be unlocked
                  intAt(local_stakeUnlocks, index.load()
                        ) <= Global.latest_timestamp(),

                  # make sure stake at provided index was not already unstaked
                  intAt(local_claimed, index.load()) == Int(0),
              ),
          ),
          setIntAt(local_claimed, index.load(), mainReward.load()),

          # send main reward asset
          InnerTxnBuilder.Begin(),
          InnerTxnBuilder.SetFields({
              TxnField.type_enum: TxnType.AssetTransfer,
              TxnField.asset_receiver: Txn.sender(),
              TxnField.asset_amount: mainReward.load(),
              TxnField.xfer_asset: assetId(planId.load()),
              TxnField.fee: Int(0),
          }),
          InnerTxnBuilder.Submit(),


          # send secondary reward asset
          If(
              Gt(secondaryReward.load(), Int(0)),
              Seq(
                  InnerTxnBuilder.Begin(),
                  InnerTxnBuilder.SetFields({
                      TxnField.type_enum: TxnType.AssetTransfer,
                      TxnField.asset_receiver: Txn.sender(),
                      TxnField.asset_amount: secondaryReward.load(),
                      TxnField.xfer_asset: secondaryRewardAssetId(planId.load()),
                      TxnField.fee: Int(0),
                  }),
                  InnerTxnBuilder.Submit(),
                  Approve(),
              )
          ),
      )

    @Subroutine(TealType.none)
    def optinFT():
      return Seq(
          Assert(
              And(
                  # restrict for owner only
                  App.globalGet(global_creator) == Txn.sender(),

                  # check that fee is big enough
                  Txn.fee() >= Global.min_txn_fee() * Int(2),
              )
          ),
          InnerTxnBuilder.Begin(),
          InnerTxnBuilder.SetFields({
              TxnField.type_enum: TxnType.AssetTransfer,
              TxnField.asset_receiver: Global.current_application_address(),
              TxnField.asset_amount: Int(0),
              TxnField.xfer_asset: Txn.assets[0],
              TxnField.fee: Int(0),
          }),
          InnerTxnBuilder.Submit(),
          Approve(),
      )

    @Subroutine(TealType.none)
    def withdraw():
      return Seq(
          Assert(
              And(
                  # restrict for owner only
                  App.globalGet(global_creator) == Txn.sender(),

                  # check that fee is big enough
                  Txn.fee() >= Global.min_txn_fee() * Int(2),

                  # check that we have 2 args
                  Txn.application_args.length() == Int(2),
              )
          ),
          InnerTxnBuilder.Begin(),
          InnerTxnBuilder.SetFields({
              TxnField.type_enum: TxnType.AssetTransfer,
              TxnField.asset_receiver: Txn.sender(),
              TxnField.asset_amount: Btoi(Txn.application_args[1]),
              TxnField.xfer_asset: Txn.assets[0],
              TxnField.fee: Int(0),
          }),
          InnerTxnBuilder.Submit(),
          Approve(),
      )

    return program.event(
        init=Seq(
            App.globalPut(global_creator, Txn.sender()),
            Approve()
        ),
        opt_in=Seq(
            App.localPut(Txn.sender(), local_stakePlanIds, Bytes("")),
            App.localPut(Txn.sender(), local_stakeAmounts, Bytes("")),
            App.localPut(Txn.sender(), local_stakeUnlocks, Bytes("")),
            App.localPut(Txn.sender(), local_claimed, Bytes("")),
            Approve(),
        ),
        no_op=Seq(
            Cond(
                [Txn.application_args[0] == op_stake, stake()],
                [Txn.application_args[0] == op_unstake, unstake()],
                [Txn.application_args[0] == op_optinFT, optinFT()],
                [Txn.application_args[0] == op_withdraw, withdraw()],
            ),
            Reject(),
        )
    )


def clear():
    return Approve()
