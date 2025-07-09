const plausibleMock = jest.fn();

plausibleMock.mockImplementationOnce = function (impl) {
    const originalMock = this;
    const onceMock = jest.fn(impl);
    this.mockImplementation((...args) => {
        if (onceMock.mock.calls.length === 0) {
            return onceMock(...args);
        }
        return originalMock(...args);
    });
};

module.exports = {
    default: plausibleMock,
};
