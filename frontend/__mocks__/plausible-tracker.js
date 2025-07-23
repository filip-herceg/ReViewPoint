const plausibleMock = jest.fn();

plausibleMock.mockImplementationOnce = function (impl) {
  const onceMock = jest.fn(impl);
  this.mockImplementation((...args) => {
    if (onceMock.mock.calls.length === 0) {
      return onceMock(...args);
    }
    return this(...args);
  });
};

module.exports = {
  default: plausibleMock,
};
