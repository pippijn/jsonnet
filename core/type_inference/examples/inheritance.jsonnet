{
    local person = {
        name: 'unknown',
        has_friend: true
    },
    student: person { 
        name: 'Ali', 
        age: 19,
        best_friend: person {
            age: 18,
        }  
    },
}