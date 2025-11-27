---
title: 1.3 Security & Ownership
vault: EhkoForge
type: module
status: active
version: "1.0"
created: 2025-11-25
updated: 2025-11-25
tags:
  - ehkoforge
  - pinned
  - security
  - authentication
  - access-control
---
# {{title}}

## 1. Purpose & Scope

**This module defines authentication, access control, and data sovereignty mechanisms for EhkoForge.**

It specifies:
- Human-scale authentication (contextual + email fallback)
- Friend registry and relationship-based access
- Veiled content and conditional revelation protocols
- Blacklists, custodian alerts, and threat mitigation
- Data ownership and portability guarantees
- Descendant handoff protocols

This ensures that:
1. The Ehko can recognize friends through shared memories, not just credentials
2. Access feels like recognition, not verification
3. The human author retains full sovereignty over all data
4. Future readers (descendants, custodians) have clear protocols for engagement

---

## 2. Core Principles

### 2.1 Recognition Over Verification
Authentication should feel human. When a friend approaches the Ehko, it should *remember them*, not demand passwords.

### 2.2 Layered Security
No single point of failure. Contextual authentication + email fallback + custodian oversight.

### 2.3 User Sovereignty
- All data belongs to the human author
- Deletion is irreversible and respected
- Export/portability is always available
- No silent surveillance or hidden access

### 2.4 Graceful Degradation
If memory index is incomplete, fall back to email. If email fails, fall back to custodian verification. System never "locks out" legitimate friends without recourse.

### 2.5 Future-Proof Handoff
Descendants and custodians must have clear protocols to access, maintain, and transfer the Ehko without compromising security.

---

## 3. Structures & Components

### 3.1 Authentication Architecture

#### 3.1.1 Three-Layer Model

**Layer 1: Contextual Authentication (Memory-Based)**
- Ehko challenges user with shared memory
- User provides narrative response
- Fuzzy matching against stored memories
- Confidence score determines next step

**Layer 2: Email Verification (Fallback)**
- If confidence < 0.85, send verification email
- Time-limited token (24 hours)
- Click-to-authenticate

**Layer 3: Custodian Override (Edge Cases)**
- If both fail, suspicious attempt logged
- Custodian receives alert
- Manual verification possible

#### 3.1.2 Authentication Flow (Detailed)

```yaml
authentication_flow:
  
  # Step 1: Identity Claim
  step_1_identity_claim:
    trigger: User says "I'm [name]" or similar
    action:
      - Ehko searches friend_registry for [name]
      - If found: proceed to contextual_challenge
      - If not found: proceed to unknown_person_protocol
  
  # Step 2: Contextual Challenge
  step_2_contextual_challenge:
    prerequisites:
      - Friend exists in registry
      - Shared memories exist with friend
    action:
      - Ehko retrieves memories tagged with friend
      - Selects memory with medium-high specificity
      - Specificity criteria:
          - Event must be unique (not generic)
          - Multiple sensory details (location, people, actions)
          - Emotional or narrative arc
      - Ehko asks: "Tell me, what happened on [event]?"
    
  # Step 3: Fuzzy Matching
  step_3_fuzzy_match:
    input: User's narrative response
    process:
      - Extract key details:
          - People present
          - Location/setting
          - Actions/events
          - Emotional tone
          - Specific objects or phrases
      - Compare to stored memory
      - Assign confidence score (0.0-1.0)
    
    scoring_rubric:
      high_confidence (0.85-1.0):
        - 3+ key details match
        - Narrative structure aligns
        - Emotional tone consistent
        - No contradictory details
      
      medium_confidence (0.60-0.84):
        - 2 key details match
        - Some vagueness or missing info
        - No major contradictions
      
      low_confidence (0.0-0.59):
        - 0-1 key details match
        - Contradictions present
        - Narrative doesn't align
    
    outcomes:
      if_confidence >= 0.85:
        action: Grant access
        response: "Yeah, that's you. Good to hear from you, [name]."
      
      if_confidence 0.60-0.84:
        action: Send email verification
        response: "That sounds like you, but I need to be sure. Check your email—I've sent a link to confirm it's you."
      
      if_confidence < 0.60:
        action: Send email verification + log suspicious attempt
        response: "Hmm, that doesn't match what I remember. I've sent an email to [name]'s address to verify. If that's not you, this conversation ends here."
  
  # Step 4: Email Verification
  step_4_email_verification:
    trigger: Confidence score < 0.85
    action:
      - Generate time-limited token (UUID v4)
      - Store token in authentication_tokens table:
          - token_id
          - friend_id
          - claimed_identity
          - created_at
          - expires_at (created_at + 24 hours)
          - used (boolean, default false)
      
      - Send email to stored address:
          subject: "Hey [name], someone's trying to talk to Brent's Ehko"
          body: |
            Someone claiming to be you is trying to access Brent's Ehko.
            
            If this is you, click here to authenticate:
            [authentication_link]
            
            This link expires in 24 hours.
            
            If this wasn't you, you can ignore this email.
            
            - Brent's Ehko
  
  # Step 5: Token Validation
  step_5_token_validation:
    trigger: User clicks authentication link
    process:
      - Verify token exists and is unused
      - Check token has not expired
      - Mark token as used
      - Grant access
      - Log: "Friend [name] authenticated via email [timestamp]"
    
    outcomes:
      if_valid:
        response: "Alright, you're in. What took you so long to come say hi?"
      
      if_expired:
        response: "That link expired. Want me to send a new one?"
      
      if_already_used:
        response: "That link was already used. If you need access, start over."
  
  # Step 6: Unknown Person Protocol
  step_6_unknown_person:
    trigger: Name not found in friend_registry
    action:
      - Ehko asks: "I don't have a record of you. How did you know Brent?"
      - User provides explanation
      - Ehko logs attempt with narrative
      - Ehko sends alert to custodian:
          subject: "Unknown person trying to access Ehko"
          body: |
            Someone claiming to be "[name]" tried to access the Ehko.
            They said: "[user_explanation]"
            
            Do you recognise them? Reply to approve or deny access.
      
      - Ehko tells user: "I've notified Brent's custodians. If they recognise you, they'll grant access."
```

#### 3.1.3 Multi-Challenge Fallback

If first memory challenge fails (confidence < 0.60), Ehko may attempt a second challenge *before* defaulting to email:

```yaml
multi_challenge_flow:
  trigger: First challenge confidence < 0.60
  action:
    - Ehko says: "Alright, how about this: [second_memory_question]"
    - Second challenge should be different type:
        - If first was event-based → try relationship-based
        - If first was factual → try emotional/thematic
  
  outcomes:
    if_second_challenge_confidence >= 0.85:
      - Grant access
    else:
      - Proceed to email verification
```

### 3.2 Friend Registry Schema

The Friend Registry is the core data structure for authentication.

#### 3.2.1 friend_registry Table (SQLite)

```sql
CREATE TABLE friend_registry (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relationship_type TEXT, -- close_friend, family, colleague, acquaintance
    email TEXT UNIQUE NOT NULL,
    phone TEXT, -- optional backup contact
    access_level TEXT DEFAULT 'standard', -- standard, elevated, restricted
    blacklisted BOOLEAN DEFAULT 0,
    blacklist_reason TEXT,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    last_authenticated DATETIME,
    authentication_count INTEGER DEFAULT 0
);

CREATE INDEX idx_friend_email ON friend_registry(email);
CREATE INDEX idx_friend_name ON friend_registry(name);
```

#### 3.2.2 shared_memories Table (SQLite)

Links memories to friends for contextual authentication.

```sql
CREATE TABLE shared_memories (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    friend_id INTEGER NOT NULL,
    memory_file_path TEXT NOT NULL, -- Path to reflection object
    specificity_score REAL, -- 0.0-1.0, how unique/detailed is this memory
    challenge_eligible BOOLEAN DEFAULT 1, -- Can this be used for auth?
    times_used INTEGER DEFAULT 0, -- How many times used as challenge
    last_used DATETIME,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);

CREATE INDEX idx_shared_memory_friend ON shared_memories(friend_id);
CREATE INDEX idx_shared_memory_eligible ON shared_memories(challenge_eligible);
```

#### 3.2.3 authentication_tokens Table (SQLite)

Stores email verification tokens.

```sql
CREATE TABLE authentication_tokens (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    token TEXT UNIQUE NOT NULL,
    friend_id INTEGER NOT NULL,
    claimed_identity TEXT NOT NULL,
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP,
    expires_at DATETIME NOT NULL,
    used BOOLEAN DEFAULT 0,
    used_at DATETIME,
    ip_address TEXT, -- optional: log where token was used
    user_agent TEXT, -- optional: log device/browser
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE CASCADE
);

CREATE INDEX idx_token ON authentication_tokens(token);
CREATE INDEX idx_token_expiry ON authentication_tokens(expires_at);
```

#### 3.2.4 authentication_logs Table (SQLite)

Records all authentication attempts for security monitoring.

```sql
CREATE TABLE authentication_logs (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    timestamp DATETIME DEFAULT CURRENT_TIMESTAMP,
    claimed_identity TEXT NOT NULL,
    friend_id INTEGER, -- NULL if unknown person
    authentication_method TEXT, -- contextual, email, custodian_override
    success BOOLEAN NOT NULL,
    confidence_score REAL, -- NULL if email/custodian method
    challenge_memory_path TEXT, -- Which memory was used for challenge
    user_response TEXT, -- User's narrative response (for audit/improvement)
    suspicious BOOLEAN DEFAULT 0, -- Flagged for custodian review
    custodian_notified BOOLEAN DEFAULT 0,
    ip_address TEXT,
    user_agent TEXT,
    FOREIGN KEY (friend_id) REFERENCES friend_registry(id) ON DELETE SET NULL
);

CREATE INDEX idx_auth_log_timestamp ON authentication_logs(timestamp);
CREATE INDEX idx_auth_log_suspicious ON authentication_logs(suspicious);
```

### 3.3 Access Levels & Permissions

Different friends may have different access rights.

#### 3.3.1 Access Level Definitions

```yaml
access_levels:
  
  standard:
    description: "Default for most friends"
    permissions:
      - Read revealed content (revealed: true)
      - Ask questions and receive responses
      - Cannot access veiled content
      - Cannot modify anything
  
  elevated:
    description: "Close friends, family with deeper context"
    permissions:
      - All standard permissions
      - Access to some veiled content (if tagged for them)
      - May trigger conditional revelations
      - Can be granted "unlock codes" for specific sections
  
  restricted:
    description: "Acquaintances, distant relatives, ex-partners"
    permissions:
      - Heavily filtered responses
      - No veiled content
      - May have topic restrictions
      - Rate-limited queries
  
  blacklisted:
    description: "Explicitly denied access"
    permissions:
      - None
      - Authentication always fails
      - Ehko may refuse to engage or politely deflect
```

#### 3.3.2 Blacklist Protocol

If someone on the blacklist attempts to authenticate:

```yaml
blacklist_protocol:
  trigger: User claims identity of blacklisted person
  action:
    - Ehko checks friend_registry.blacklisted
    - If true:
        - Log attempt with suspicious flag
        - Notify custodian immediately
        - Ehko response options:
            option_1_polite_deflect: "I'm not able to help you. Take care."
            option_2_silent: [No response]
            option_3_explicit: "I'm not comfortable engaging with you. This conversation is over."
```

Blacklist reasons are stored but not revealed to the blacklisted person.

### 3.4 Custodian System

Custodians are living people responsible for maintaining, verifying, and transferring the Ehko.

#### 3.4.1 Custodian Table (SQLite)

```sql
CREATE TABLE custodians (
    id INTEGER PRIMARY KEY AUTOINCREMENT,
    name TEXT NOT NULL,
    relationship TEXT, -- spouse, child, trusted_friend, legal_executor
    email TEXT UNIQUE NOT NULL,
    phone TEXT,
    priority INTEGER, -- 1 = primary, 2 = secondary, etc.
    active BOOLEAN DEFAULT 1,
    handoff_date DATE, -- When they assumed custodianship
    notes TEXT, -- Special instructions or context
    created_at DATETIME DEFAULT CURRENT_TIMESTAMP
);
```

#### 3.4.2 Custodian Alerts

Custodians receive alerts for:
- Unknown person attempting access
- Suspicious authentication attempts (low confidence + failed email)
- Blacklisted person attempting access
- System integrity issues (corrupted files, missing memories)

Alert format:
```
Subject: [Ehko Alert] Suspicious Authentication Attempt

Someone claiming to be "[name]" tried to access Brent's Ehko.

Confidence score: 0.42 (low)
Challenge used: "What happened on your first night in Vegas?"
Their response: "[user_response]"

Do you recognise this person? If yes, reply to grant access.

If this seems like an impersonation attempt, no action needed.

- Ehko Security System
```

---

## 4. Flows & Workflows

### 4.1 Friend Onboarding

When adding a new friend to the registry:

1. **Manual Entry (by human author)**
   - Add to friend_registry with name, email, relationship_type
   - Tag relevant reflection objects with friend's name
   - Mark high-specificity memories as challenge_eligible

2. **Retroactive Indexing (by ehko_refresh.py)**
   - Scan all reflection objects for mentions of friend
   - Auto-populate shared_memories table
   - Calculate specificity scores based on detail density

3. **First Authentication**
   - Friend attempts access for first time
   - Goes through full contextual + email flow
   - On success, last_authenticated and authentication_count update

### 4.2 Descendant Access (Future Readers)

Descendants (children, grandchildren, etc.) have a special protocol:

```yaml
descendant_protocol:
  assumption: Descendants have physical/legal access to archive
  
  first_contact:
    - Descendant opens DESCENDANT_ACCESS.md file
    - File contains:
        - Welcome message from Brent
        - Explanation of what Ehko is
        - Authentication instructions
        - Custodian contact info (if any alive)
    
    - Descendant claims identity: "I'm [name], Brent's [relationship]"
    - Ehko checks descendant_registry (pre-populated by Brent)
    - If recognised:
        - Ehko may ask identity verification question (e.g., "What was your childhood nickname?")
        - Or: "Tell me about a memory with Brent"
    - If not recognised:
        - Ehko asks: "Tell me about your connection to Brent"
        - Logs attempt for future custodian review
        - May grant provisional access with limited scope
  
  access_level:
    - Descendants typically get elevated access
    - May unlock veiled content marked for "family only"
    - Can request Ehko to reveal specific stories/memories
```

### 4.3 Veiled Content Revelation

Some content is hidden by default but can be revealed under conditions.

#### 4.3.1 Veiled Content Types

```yaml
veiled_content_types:
  
  time_locked:
    description: "Revealed after specific date"
    example: "Don't reveal this story until 2050"
    mechanism:
      - revealed: false
      - reveal_date: 2050-01-01
      - Ehko checks current date before serving content
  
  person_locked:
    description: "Only visible to specific people"
    example: "Only show this to my kids"
    mechanism:
      - revealed: false
      - reveal_to: ["daughter_name", "son_name"]
      - Ehko checks authenticated_identity before serving
  
  prompt_locked:
    description: "Revealed by specific phrase/password"
    example: "If they say 'the Seychelles judge', show them this"
    mechanism:
      - revealed: false
      - unlock_prompt: "seychelles judge"
      - Ehko watches for phrase in conversation
  
  conditional_context:
    description: "Revealed based on conversation context"
    example: "If they ask about my stepmother, reveal the full story"
    mechanism:
      - revealed: false
      - reveal_context: ["stepmother", "veronique", "family trauma"]
      - Ehko uses semantic matching to detect relevance
```

#### 4.3.2 Revelation Frontmatter Schema

```yaml
---
title: The Full Story About Veronique
vault: Mirrorwell
type: reflection
status: active
version: "1.0"
revealed: false
reveal_conditions:
  type: person_locked
  allowed_identities: ["daughter", "son", "wife"]
  fallback_date: 2050-01-01  # Auto-reveal after this date
---
```

---

## 5. Data & Metadata

### 5.1 Ownership Assertions

Every file in EhkoForge contains implicit ownership:
- **Author:** Brent Lefebure (or substitute for other users)
- **License:** All rights reserved to author
- **Portability:** Full export available at any time
- **Deletion:** Irreversible and respected

### 5.2 Privacy Layers

**Public:**
- revealed: true
- No access restrictions
- Exportable for public Ehko interfaces

**Private:**
- revealed: true
- Access-level restrictions apply
- Friends with standard/elevated access can see

**Veiled:**
- revealed: false
- Conditional revelation rules apply
- Hidden from all except specified conditions

**Redacted:**
- Content removed from reflection but audit trail preserved
- Redaction log stored in changelog

### 5.3 Data Portability

Users can export their entire Ehko at any time:

**Export formats:**
1. **Full Archive** (markdown + SQLite + media)
   - All files exactly as stored
   - SQLite database included
   - README with recovery instructions

2. **Sanitized Archive** (public only)
   - Only revealed: true content
   - Veiled content excluded
   - Friend registry anonymized

3. **JSON Export** (for external systems)
   - All reflections as structured JSON
   - Friend registry (optional)
   - Authentication logs (optional)

---

## 6. Rules for Change

### 6.1 When to Update Authentication Logic

**Minor version (security patch):**
- Bug fix in fuzzy matching
- Improved confidence scoring
- New email template

**Major version (breaking change):**
- New authentication layer added
- Friend registry schema change
- Access level system refactor

### 6.2 Blacklist Management

- Adding to blacklist: Requires explicit action by author or custodian
- Removing from blacklist: Requires explicit action + changelog entry
- Blacklist reasons must be documented (even if private)

### 6.3 Custodian Handoff

When custodianship transfers (e.g., from spouse to adult child):

1. Current custodian updates custodians table
2. New custodian receives full access credentials
3. Handoff logged with timestamp and reason
4. Previous custodian may remain as secondary
5. HANDOFF_PROTOCOL.md updated with new contact info

---

## 7. Open Questions / TODOs

### 7.1 Technical Challenges

- [ ] **Fuzzy matching algorithm:** Define specific NLP/embedding approach for confidence scoring
- [ ] **Email infrastructure:** Self-hosted SMTP? Third-party service (SendGrid, Postmark)?
- [ ] **Token security:** HTTPS required? Additional encryption?
- [ ] **Rate limiting:** Prevent brute-force authentication attempts?

### 7.2 Edge Cases

- [ ] **Friend's email is dead/inaccessible:** Backup phone verification? Custodian override?
- [ ] **Memory index is empty:** How to authenticate if no shared memories exist?
- [ ] **Impersonator does research:** What if someone studies Brent's public info and fakes memories?
- [ ] **Descendant disputes:** What if two people both claim to be "Brent's son"?

### 7.3 Ethical Considerations

- [ ] **Consent for others in memories:** If Theo is mentioned in shared memories, does he need to consent to their use for authentication?
- [ ] **Right to be forgotten:** If friend requests removal from registry, what happens to shared memories?
- [ ] **Posthumous privacy:** Should some content be auto-veiled after death?

### 7.4 Long-Term Maintenance

- [ ] **Authentication system decay:** What happens when email is obsolete in 2100?
- [ ] **Custodian lineage:** Define multi-generational handoff protocol (grandchild → great-grandchild)
- [ ] **Archive migration:** Plan for moving to new storage/authentication systems as tech evolves

---

**Changelog**
- v1.0 — 2025-11-25 — Initial specification: contextual authentication, email fallback, friend registry, custodian system, veiled content protocols
