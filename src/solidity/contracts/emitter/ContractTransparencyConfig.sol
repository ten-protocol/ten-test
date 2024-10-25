interface ContractTransparencyConfig {
    enum Field {
        TOPIC1, TOPIC2, TOPIC3,
        SENDER,  // tx.origin - msg.sender
        EVERYONE // the event is public - visible to everyone
    }

    enum ContractCfg {
        TRANSPARENT, // internal state via getStorageAt is accessible to everyone, all events are public
        PRIVATE      // internal state is hidden, and events can be configured individually
    }

    struct EventLogConfig {
        bytes32 eventSignature; // the event signature hash
        Field[] visibleTo;      // list of fields denoting who can see the event when private
    }

    struct VisibilityConfig {
        ContractCfg contractCfg;
        EventLogConfig[] eventLogConfigs;
    }

    function visibilityRules() external pure returns (VisibilityConfig memory);
}