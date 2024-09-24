interface ContractTransparencyConfig {
    // configuration per event log type
    struct EventLogConfig {
        bytes eventSignature;
        bool isPublic;        // everyone can see and query for this event
        bool topic1CanView;   // if private and true the address from topic1 is an EOA that can view
        bool topic2CanView;   // if private and true the address from topic2 is an EOA that can view
        bool topic3CanView;   // if private and true the address from topic2 is an EOA that can view
        bool visibleToSender; // if true, the tx signer will see this event
    }

    struct VisibilityConfig {
        bool isTransparent;  // if true getStorageAt will be accessible to everyone, and all events will be public
        EventLogConfig[] eventLogConfigs; // if an event is not included, semantics fall back to previous behaviour
    }

    // keep the logic independent of the environment
    function visibilityRules() external pure returns (VisibilityConfig memory);
}