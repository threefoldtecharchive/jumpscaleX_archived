@0xd80b12c2d2d132c5;

struct Issue {
    title @0 :Text;
    repo @1 :Text;
    milestone @2 :Text; #is name of milestone
    assignees @3 :List(Text); #keys of user
    isClosed @4 :Bool;
    comments @5 :List(Comment);
    struct Comment{
        owner @0 :Text;
        comment @1 :Text;
        modTime @2 :UInt32;
    }
    labels @6 :List(Text);
    content @7 :Text;
    organization @8 :Text;
    modTime @9 :UInt32;
    creationTime @10 :UInt32;
    gitHostRefs @11 :List(GitHostRef);
    struct GitHostRef{
        name @0 :Text;
        id @1 :UInt32;
        url @2 :Text;
    }
    state @12: State;
    enum State {
        new   @0;
        inprogress    @1;
        resolved  @2;
        wontfix @3;
        question  @4;
        closed  @5;
    }

    priority @13: Priority;
    enum Priority {
        minor   @0;
        normal    @1;
        major  @2;
        critical @3;
    }

    type @14: Type;
    enum Type {
        unknown   @0;
        alert   @1;
        bug    @2;
        doc  @3;
        feature @4;
        incident   @5;
        question    @6;
        request  @7;
        story @8;
        task   @9;
    }
    inGithub @15: Bool;

}

struct Organization{
    owners @0 :List(Text);
    name @1 :Text;
    description @2 :Text;
    nrIssues @3 :UInt16;
    nrRepos @4 :UInt16;
    gitHostRefs @5 :List(GitHostRef);
    struct GitHostRef{
        name @0 :Text;
        id @1 :UInt32;
        url @2: Text;
    }
    members @6 :List(Member);
    struct Member{
        key @0 :Text;
        access @1:UInt16;
        name @2: Text;
    }
    repos @7 :List(Repo);
    struct Repo{
        key @0 :Text;
        name @1: Text;
        access @2:UInt16;
    }
    inGithub @8: Bool;

}

struct Repo{
    owner @0 :Text;
    name @1 :Text;
    description @2 :Text;
    nrIssues @3 :UInt16;
    nrMilestones @4 :UInt16;
    members @5 :List(Member);
    struct Member{
        userKey @0 :Text;
        access @1 :UInt16;
    }
    gitHostRefs @6 :List(GitHostRef);
    struct GitHostRef{
        name @0 :Text;
        id @1 :UInt32;
        url @2: Text;
    }
    inGithub @7: Bool;
}

struct User{
    name @0 :Text; #as to be used to represent in UI
    fullname @1 :Text;
    email @2 :Text; #will be used for escalation
    gitHostRefs @3 :List(GitHostRef);
    struct GitHostRef{
        name @0 :Text;
        id @1 :UInt32;
        url @2: Text;
    }
    githubId @4 :Text; #e.g. despiegk
    telegramId @5: Text;#e.g. despiegk
    iyoId@6: Text;#e.g. despiegk
    inGithub @7: Bool;
}
