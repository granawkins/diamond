export type State = {
    legs: {
        [key: string]: {
            [key: string]: number
        }
    }
    battery: {
        percentage: number
        status: string
    }
}

export type Vec3 = [number, number, number]

export type DHParams = {
    alpha: number
    a: number
    d: number
    theta: number
}
