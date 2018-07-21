; ModuleID = 'out/password.bc'
target datalayout = "e-p:64:64:64-i1:8:8-i8:8:8-i16:16:16-i32:32:32-i64:64:64-f32:32:32-f64:64:64-v64:64:64-v128:128:128-a0:0:64-s0:64:64-f80:128:128-n8:16:32:64-S128"
target triple = "x86_64-unknown-linux-gnu"

@.str = private unnamed_addr constant [14 x i8] c"newlyappended\00", align 1
@.str1 = private unnamed_addr constant [4 x i8] c"Yes\00", align 1
@.str2 = private unnamed_addr constant [3 x i8] c"No\00", align 1
@.str3 = private unnamed_addr constant [17 x i8] c"Password found!\0A\00", align 1

; Function Attrs: nounwind uwtable
define i32 @get_length(i8* %str) #0 {
entry:
  %str.addr = alloca i8*, align 8
  store i8* %str, i8** %str.addr, align 8
  %0 = load i8** %str.addr, align 8
  %call = call i64 @strlen(i8* %0) #4
  %conv = trunc i64 %call to i32
  ret i32 %conv
}

; Function Attrs: nounwind readonly
declare i64 @strlen(i8*) #1

; Function Attrs: nounwind uwtable
define void @append_string(i8* %str) #0 {
entry:
  %str.addr = alloca i8*, align 8
  store i8* %str, i8** %str.addr, align 8
  %0 = load i8** %str.addr, align 8
  %call = call i8* @strcat(i8* %0, i8* getelementptr inbounds ([14 x i8]* @.str, i32 0, i32 0)) #5
  ret void
}

; Function Attrs: nounwind
declare i8* @strcat(i8*, i8*) #2

; Function Attrs: nounwind uwtable
define void @a1(i32 %x) #0 {
entry:
  %x.addr = alloca i32, align 4
  store i32 %x, i32* %x.addr, align 4
  %call = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([4 x i8]* @.str1, i32 0, i32 0))
  call void @a2(i32 0)
  ret void
}

declare i32 @printf(i8*, ...) #3

; Function Attrs: nounwind uwtable
define void @a2(i32 %y) #0 {
entry:
  %y.addr = alloca i32, align 4
  store i32 %y, i32* %y.addr, align 4
  %call = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([3 x i8]* @.str2, i32 0, i32 0))
  call void @a1(i32 0)
  ret void
}

; Function Attrs: nounwind uwtable
define i32 @check_password(i8* %buf) #0 {
entry:
  %retval = alloca i32, align 4
  %buf.addr = alloca i8*, align 8
  %len = alloca i32, align 4
  store i8* %buf, i8** %buf.addr, align 8
  %0 = load i8** %buf.addr, align 8
  %call = call i32 @get_length(i8* %0)
  store i32 %call, i32* %len, align 4
  %1 = load i8** %buf.addr, align 8
  %arrayidx = getelementptr inbounds i8* %1, i64 0
  %2 = load i8* %arrayidx, align 1
  %conv = sext i8 %2 to i32
  %cmp = icmp eq i32 %conv, 104
  br i1 %cmp, label %land.lhs.true, label %if.end

land.lhs.true:                                    ; preds = %entry
  %3 = load i8** %buf.addr, align 8
  %arrayidx2 = getelementptr inbounds i8* %3, i64 1
  %4 = load i8* %arrayidx2, align 1
  %conv3 = sext i8 %4 to i32
  %cmp4 = icmp eq i32 %conv3, 101
  br i1 %cmp4, label %land.lhs.true6, label %if.end

land.lhs.true6:                                   ; preds = %land.lhs.true
  %5 = load i8** %buf.addr, align 8
  %arrayidx7 = getelementptr inbounds i8* %5, i64 2
  %6 = load i8* %arrayidx7, align 1
  %conv8 = sext i8 %6 to i32
  %cmp9 = icmp eq i32 %conv8, 108
  br i1 %cmp9, label %land.lhs.true11, label %if.end

land.lhs.true11:                                  ; preds = %land.lhs.true6
  %7 = load i8** %buf.addr, align 8
  %arrayidx12 = getelementptr inbounds i8* %7, i64 3
  %8 = load i8* %arrayidx12, align 1
  %conv13 = sext i8 %8 to i32
  %cmp14 = icmp eq i32 %conv13, 108
  br i1 %cmp14, label %land.lhs.true16, label %if.end

land.lhs.true16:                                  ; preds = %land.lhs.true11
  %9 = load i8** %buf.addr, align 8
  %arrayidx17 = getelementptr inbounds i8* %9, i64 4
  %10 = load i8* %arrayidx17, align 1
  %conv18 = sext i8 %10 to i32
  %cmp19 = icmp eq i32 %conv18, 111
  br i1 %cmp19, label %if.then, label %if.end

if.then:                                          ; preds = %land.lhs.true16
  store i32 1, i32* %retval
  br label %return

if.end:                                           ; preds = %land.lhs.true16, %land.lhs.true11, %land.lhs.true6, %land.lhs.true, %entry
  %11 = load i8** %buf.addr, align 8
  call void @append_string(i8* %11)
  store i32 0, i32* %retval
  br label %return

return:                                           ; preds = %if.end, %if.then
  %12 = load i32* %retval
  ret i32 %12
}

; Function Attrs: nounwind uwtable
define i32 @main(i32 %argc, i8** %argv) #0 {
entry:
  %retval = alloca i32, align 4
  %argc.addr = alloca i32, align 4
  %argv.addr = alloca i8**, align 8
  %x = alloca i32, align 4
  store i32 0, i32* %retval
  store i32 %argc, i32* %argc.addr, align 4
  store i8** %argv, i8*** %argv.addr, align 8
  %0 = load i32* %argc.addr, align 4
  %cmp = icmp slt i32 %0, 2
  br i1 %cmp, label %if.then, label %if.end

if.then:                                          ; preds = %entry
  store i32 1, i32* %retval
  br label %return

if.end:                                           ; preds = %entry
  %1 = load i8*** %argv.addr, align 8
  %arrayidx = getelementptr inbounds i8** %1, i64 1
  %2 = load i8** %arrayidx, align 8
  %call = call i32 @get_length(i8* %2)
  store i32 %call, i32* %x, align 4
  %3 = load i8*** %argv.addr, align 8
  %arrayidx1 = getelementptr inbounds i8** %3, i64 1
  %4 = load i8** %arrayidx1, align 8
  %call2 = call i32 @check_password(i8* %4)
  %tobool = icmp ne i32 %call2, 0
  br i1 %tobool, label %if.then3, label %if.end5

if.then3:                                         ; preds = %if.end
  %call4 = call i32 (i8*, ...)* @printf(i8* getelementptr inbounds ([17 x i8]* @.str3, i32 0, i32 0))
  store i32 0, i32* %retval
  br label %return

if.end5:                                          ; preds = %if.end
  store i32 1, i32* %retval
  br label %return

return:                                           ; preds = %if.end5, %if.then3, %if.then
  %5 = load i32* %retval
  ret i32 %5
}

attributes #0 = { nounwind uwtable "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #1 = { nounwind readonly "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #2 = { nounwind "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #3 = { "less-precise-fpmad"="false" "no-frame-pointer-elim"="true" "no-frame-pointer-elim-non-leaf" "no-infs-fp-math"="false" "no-nans-fp-math"="false" "stack-protector-buffer-size"="8" "unsafe-fp-math"="false" "use-soft-float"="false" }
attributes #4 = { nounwind readonly }
attributes #5 = { nounwind }

!llvm.ident = !{!0}

!0 = metadata !{metadata !"clang version 3.4 (335426)"}
